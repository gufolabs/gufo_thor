# ---------------------------------------------------------------------
# Gufo Thor: nginx service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
nginx service.

Attributes:
    nginx: nginx service singleton.
"""

# Python modules
import http.client
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..error import CancelExecution
from ..log import logger
from .base import BaseService
from .login import login
from .traefik import traefik

HTTP_OK = 200


@dataclass
class DomainInfo(object):
    """
    Information for preconfigured domains.

    Attributes:
        domain: Domain name.
        csr_proxy: CSR Proxy URL
        subject: CSR subject.
    """

    domain: str
    csr_proxy: str
    subject: str


DOMAINS = {
    "go.getnoc.com": DomainInfo(
        domain="go.getnoc.com",
        csr_proxy="csr-proxy.getnoc.com",
        subject="CN=go.getnoc.com",
    )
}


class NginxService(BaseService):
    """nginx service."""

    name = "nginx"
    dependencies = (traefik, login)
    compose_image = "nginx:stable"
    SUBJ_PATH = "etc/nginx/ssl/domain_name.txt"
    RSA_KEY_SIZE = 4096
    CERT_DAYS = 3650
    compose_etc_dirs = [Path("nginx", "conf.d"), Path("nginx", "ssl")]

    def get_compose_volumes(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """Get volumes section."""
        r = ["./etc/nginx:/etc/nginx"]
        if config.noc.path:
            # Use /ui from repo
            r += [f"{config.noc.path}/ui:/opt/noc/ui"]
        else:
            # Use /ui from container
            r.append("static:/opt/noc/ui")
        return r

    def get_compose_networks(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        """Get networks section."""
        return {
            "aliases": ["nginx", config.expose.domain_name],
        }

    def get_compose_ports(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """Get ports section."""
        return [f"{config.expose.port}:443"]

    def prepare_compose_config(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        """Geerate configuration files."""
        cfg_root = Path("etc", "nginx")
        self.render_file(cfg_root / "nginx.conf", "nginx.conf")
        self.render_file(cfg_root / "mime.types", "mime.types")
        self.render_file(
            cfg_root / "conf.d" / "noc.conf",
            "noc.conf",
            domain_name=config.expose.domain_name,
            port=config.expose.port,
        )
        # Prepare TLS certificates
        if self._to_rebuild_certificate(config):
            self._rebuild_certificate(config)

    def _to_rebuild_certificate(self: "NginxService", config: Config) -> bool:
        """Check if SSL certificate must be rebuilt."""
        if not os.path.exists(self.SUBJ_PATH):
            return True
        with open(self.SUBJ_PATH) as fp:
            return fp.read() != self.get_cert_subj(config)

    def get_cert_subj(self: "NginxService", config: Config) -> str:
        """Get certificate subj."""
        return f"CN={config.expose.domain_name}"

    def _get_signed_csr(
        self: "NginxService", csr_proxy: str, csr: bytes
    ) -> bytes:
        """
        Sign certificate via CSR Proxy.

        Args:
            csr_proxy: CSR Proxy base url.
            csr: CSR body.

        Returns:
            Siged CSR.
        """
        conn = http.client.HTTPSConnection(csr_proxy)
        conn.request("POST", "/v1/sign", body=csr)
        resp = conn.getresponse()
        if resp.status == HTTP_OK:
            return resp.read()
        logger.error("Invalid response: %s", resp.status)
        logger.error("Failed to sign certificate")
        raise CancelExecution()

    def _rebuild_certificate(self: "NginxService", config: Config) -> None:
        """Rebuild SSL certificates."""
        from gufo.acme.clients.base import AcmeClient

        key_path = "etc/nginx/ssl/noc.key"
        csr_path = "etc/nginx/ssl/noc.csr"
        cert_path = "etc/nginx/ssl/noc.crt"

        di = DOMAINS.get(config.expose.domain_name)
        if di is None:
            logger.error(
                "Certificate autogeneration is not supported for domain %s",
                config.expose.domain_name,
            )
            logger.error(
                "Either change expose.domain to one of: %s", ", ".join(DOMAINS)
            )
            logger.error(
                "Or generate private key and place it into %s", key_path
            )
            logger.error("And signed certificate into %s", cert_path)
            raise CancelExecution()
        # Generate key
        logger.warning("Generating private key: %s", key_path)
        private_key = AcmeClient.get_domain_private_key()
        with open(key_path, "wb") as fp:
            fp.write(private_key)
        # Create CSR
        logger.warning("Generating certificate signing request: %s", csr_path)
        csr = AcmeClient.get_domain_csr(config.expose.domain_name, private_key)
        with open(csr_path, "wb") as fp:
            fp.write(csr)
        # Sign CSR
        logger.warning("Signing certificate: %s", cert_path)
        cert = self._get_signed_csr(di.csr_proxy, csr)
        with open(cert_path, "wb") as fp:
            fp.write(cert)
        # Write subj
        logger.warning("Writing %s", self.SUBJ_PATH)
        with open(self.SUBJ_PATH, "w") as fp:
            fp.write(self.get_cert_subj(config))


nginx = NginxService()

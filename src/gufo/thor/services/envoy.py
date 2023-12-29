# ---------------------------------------------------------------------
# Gufo Thor: envoy service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
envoy service.

Attributes:
    eenvoy: envoy service singleton.
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
from ..utils import write_file
from .base import BaseService

HTTP_OK = 200
HTTPS = 443


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


@dataclass
class Route(object):
    """
    routes part of config.

    Attributes:
        name: Service name.
        prefix: HTTP prefix.
        disable_auth: Disable external authorization.
        prefix_rewite: Rewrite prefix, if set.
        redirect_to: Redirect to path, if matched.
    """

    name: str
    prefix: str
    disable_auth: bool
    prefix_rewrite: Optional[str] = None
    redirect_to: Optional[str] = None


class EnvoyService(BaseService):
    """envoy service."""

    name = "envoy"
    compose_image = "envoyproxy/envoy:v1.28.0"
    # compose_depends_condition = ComposeDependsCondition.HEALTHY
    # compose_healthcheck = {
    #     "test": ["CMD", "envoy", "healthcheck", "--ping"],
    #     "interval": "3s",
    #     "timeout": "2s",
    #     "retries": 3,
    # }
    compose_volumes = ["./etc/envoy/:/etc/envoy/:ro"]
    SUBJ_PATH = Path("etc", "envoy", "ssl", "domain_name.txt")
    RSA_KEY_SIZE = 4096
    CERT_DAYS = 3650

    def get_compose_networks(
        self: "EnvoyService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        """Get networks section."""
        return {
            "aliases": ["envoy", config.expose.domain_name],
        }

    def get_compose_ports(
        self: "EnvoyService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """Get ports section."""
        return [f"{config.expose.port}:443"]

    def prepare_compose_config(
        self: "EnvoyService",
        config: Config,
        svc: Optional[ServiceConfig],
        services: List["BaseService"],
    ) -> None:
        """Generate config."""
        # Generate domain_name_and_port
        if config.expose.port == HTTPS:
            domain_name_and_port = config.expose.domain_name
        else:
            domain_name_and_port = (
                f"{config.expose.domain_name}:{config.expose.port}"
            )
        # Generate routes
        routes: List[Route] = []
        for s in services:
            prefix = s.get_expose_http_prefix(config, None)
            if not prefix:
                continue
            routes.append(
                Route(
                    name=s.name,
                    prefix=prefix,
                    disable_auth=not s.require_http_auth,
                    prefix_rewrite=s.rewrite_http_prefix,
                )
            )
            if s.name == "web":
                # Add redirect to desktop
                routes.append(
                    Route(
                        name="Redirect / -> /main/desktop/",
                        prefix="/",
                        disable_auth=True,
                        redirect_to="/main/desktop/",
                    )
                )
        routes = sorted(
            routes,
            key=lambda x: "---".join(
                y if y else "zzzzzzzz" for y in x.prefix.split("/")
            )
            + f"---{not bool(x.redirect_to)}",
        )
        # Add desktop redirect, if necessary
        #
        self.render_file(
            Path("etc", "envoy", "envoy.yaml"),
            "envoy.yaml",
            domain_name=config.expose.domain_name,
            domain_name_and_port=domain_name_and_port,
            routes=routes,
            services=sorted({r.name for r in routes if not r.redirect_to}),
        )
        # Prepare TLS certificates
        if self._to_rebuild_certificate(config):
            self._rebuild_certificate(config)

    def _to_rebuild_certificate(self: "EnvoyService", config: Config) -> bool:
        """Check if SSL certificate must be rebuilt."""
        if not os.path.exists(self.SUBJ_PATH):
            return True
        with open(self.SUBJ_PATH) as fp:
            return fp.read() != self.get_cert_subj(config)

    def get_cert_subj(self: "EnvoyService", config: Config) -> str:
        """Get certificate subj."""
        return f"CN={config.expose.domain_name}"

    def _get_signed_csr(
        self: "EnvoyService", csr_proxy: str, csr: bytes
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

    def _rebuild_certificate(self: "EnvoyService", config: Config) -> None:
        """Rebuild SSL certificates."""
        from gufo.acme.clients.base import AcmeClient

        key_path = Path("etc", "envoy", "ssl", "noc.key")
        csr_path = Path("etc", "envoy", "ssl", "noc.csr")
        cert_path = Path("etc", "envoy", "ssl", "noc.crt")

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
        write_file(key_path, private_key)
        # Create CSR
        logger.warning("Generating certificate signing request: %s", csr_path)
        csr = AcmeClient.get_domain_csr(config.expose.domain_name, private_key)
        write_file(csr_path, csr)
        # Sign CSR
        logger.warning("Signing certificate: %s", cert_path)
        cert = self._get_signed_csr(di.csr_proxy, csr)
        write_file(cert_path, cert)
        # Write subj
        logger.warning("Writing %s", self.SUBJ_PATH)
        with open(self.SUBJ_PATH, "w") as fp:
            fp.write(self.get_cert_subj(config))


envoy = EnvoyService()

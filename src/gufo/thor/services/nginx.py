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
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..log import logger
from .base import BaseService
from .login import login
from .traefik import traefik


class NginxService(BaseService):
    name = "nginx"
    dependencies = (traefik, login)
    compose_image = "nginx:stable"
    SUBJ_PATH = "etc/nginx/ssl/domain_name.txt"
    RSA_KEY_SIZE = 4096
    CERT_SUBJ = "/C=IT/ST=Milano/L=Milano/O=Gufo Labs/OU=Gufo Thor"
    CERT_DAYS = 3650

    def get_compose_volumes(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        r = ["./etc/nginx:/etc/nginx"]
        if config.noc.path:
            # Use /ui from repo
            r += [f"{config.noc.path}/ui:/opt/noc/ui"]
        else:
            # Use /ui from container
            ...
        return r

    def get_compose_networks(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        return {
            "ipv4_address": "172.20.0.100",
            "aliases": ["nginx", config.expose.domain_name],
        }

    def get_compose_ports(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return [f"{config.expose.port}:443"]

    def get_compose_dirs(
        self: "NginxService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Optional[List[str]]:
        return ["etc/nginx/conf.d", "etc/nginx/ssl"]

    def prepare_compose_config(
        self: "NginxService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
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
        return f"{self.CERT_SUBJ}/CN={config.expose.domain_name}"

    def _rebuild_certificate(self: "NginxService", config: Config) -> None:
        """Rebuild SSL certificates."""
        # Generate key
        key_path = "etc/nginx/ssl/noc.key"
        logger.info("Generating private key: %s", key_path)
        subprocess.check_call(
            ["openssl", "genrsa", "-out", key_path, str(self.RSA_KEY_SIZE)]
        )
        # Create CSR
        csr_path = "etc/nginx/ssl/noc.csr"
        logger.info("Generating certificate signing request: %s", csr_path)
        subprocess.check_call(
            [
                "openssl",
                "req",
                "-key",
                key_path,
                "-new",
                "-out",
                csr_path,
                "-subj",
                self.get_cert_subj(config),
            ]
        )
        # Generate certificate
        cert_path = "etc/nginx/ssl/noc.crt"
        logger.info("Generating certificate: %s", cert_path)
        subprocess.check_call(
            [
                "openssl",
                "x509",
                "-signkey",
                key_path,
                "-in",
                csr_path,
                "-req",
                "-days",
                str(self.CERT_DAYS),
                "-out",
                cert_path,
            ]
        )
        # Write subj
        logger.info("Writing %s", self.SUBJ_PATH)
        with open(self.SUBJ_PATH, "w") as fp:
            fp.write(self.get_cert_subj(config))


nginx = NginxService()

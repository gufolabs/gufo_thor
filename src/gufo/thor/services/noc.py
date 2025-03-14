# ---------------------------------------------------------------------
# Gufo Thor: noc service
# ---------------------------------------------------------------------
# Copyright (C) 2023-24, Gufo Labs
# ---------------------------------------------------------------------
"""NocService base class."""

# Python Modules
from pathlib import Path
from typing import Any, Dict, List, Optional

# Third-party modules
import yaml

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..utils import ensure_directory, merge_dict, write_file
from .base import BaseService, ComposeDependsCondition


class NocService(BaseService):
    """Basic class for all NOC's services."""

    is_noc = True
    name = "noc"
    _config_prepared = False
    _volumes_config_prepared = False

    def get_compose_image(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        """
        Get image name.

        Use tag from service's config, if any. Otherwise use tag
        from global config.
        """
        tag = config.noc.tag
        if svc and svc.tag:
            tag = svc.tag
        return f"gufolabs/noc:{tag}"

    def get_compose_command(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        """Get command section."""
        if self.compose_command:
            return self.compose_command
        return (
            f"/usr/local/bin/python3 /opt/noc/services/{self.name}/service.py"
        )

    def get_compose_volumes(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """
        Get volumes section.

        Mount repo and custom when necessary.
        """
        # Config + crashinfo
        r: List[str] = [
            "./etc/noc/settings.yml:/opt/noc/etc/settings.yml:ro",
            "crashinfo:/var/lib/noc/cp/crashinfo/new",
        ]
        # Mount NOC repo inside an image
        if config.noc.path:
            r.append(f"{config.noc.path}:/opt/noc:cached")
        # Mount custom inside an image
        if config.noc.custom:
            r.append(f"{config.noc.custom}:/opt/noc_custom:cached")
        return r if r else None

    def get_compose_environment(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        """Get environment section."""
        r: Dict[str, str] = {}
        if config.noc.custom:
            r["NOC_PATH_CUSTOM_PATH"] = "/opt/noc_custom"
        return r if r else None

    def prepare_compose_config(
        self: "NocService",
        config: Config,
        svc: Optional[ServiceConfig],
        services: List["BaseService"],
    ) -> None:
        """
        Render configuration files.

        NB: As the NocServices is the base class for a bunch of services,
        ensure, the configuration files are rendered only once.
        """
        if self._config_prepared:
            return  # Already configured from other subclass
        # Build default config
        cfg = {
            "installation_name": config.noc.installation_name,
            "pg": {
                "db": "noc",
                "user": "noc",
                "password": "noc",
            },
            "web": {
                "theme": config.noc.theme,
            },
            "msgstream": {
                "client_class": "noc.core.msgstream.redpanda.RedPandaClient",
            },
            "redpanda": {"addresses": "kafka:9092"},
        }
        # Apply user config
        if config.noc.config:
            cfg = merge_dict(cfg, config.noc.config)
        # Write
        write_file(Path("etc", "noc", "settings.yml"), yaml.dump(cfg))
        # Ensure directories
        ensure_directory(Path("data", "crashinfo"))
        ensure_directory(Path("data", "backup"))
        # Mark as ready
        self._config_prepared = True

    def get_compose_volumes_config(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """Generate crashinfo and backup volume."""
        if self._volumes_config_prepared:
            return None  # Already prepared from other subclass
        self._volumes_config_prepared = True
        return {
            "crashinfo": {
                "driver": "local",
                "driver_opts": {
                    "type": "bind",
                    "device": "./data/crashinfo",
                    "o": "bind",
                },
            },
            "backup": {
                "driver": "local",
                "driver_opts": {
                    "type": "bind",
                    "device": "./data/backup",
                    "o": "bind",
                },
            },
        }


class NocHcService(NocService):
    """Noc service with healthcheck."""

    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD-SHELL", "curl http://$$HOSTNAME:1200/health"],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }

# ---------------------------------------------------------------------
# Gufo Thor: noc service
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
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
from .base import BaseService, ComposeDependsCondition, Role


class NocService(BaseService):
    """Basic class for all NOC's services."""

    is_noc = True
    name = "noc"
    role = Role.APP

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
        cmd = (
            f"/usr/local/bin/python3 /opt/noc/services/{self.name}/service.py"
        )
        if (
            self.is_pooled
            and self.require_pool_network
            and self._pool
            and config.pools[self._pool].address.gw
        ):
            pool_gw = config.pools[self._pool].address.gw
            cmd = " && ".join(
                (
                    "ip route delete default",
                    f"ip route add default via {pool_gw!s}",
                    cmd,
                )
            )
            return f'sh -c "{cmd}"'
        return cmd

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
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        """Get environment section."""
        r: Dict[str, str] = super().get_compose_environment(config, svc) or {}
        if config.noc.custom:
            r["NOC_PATH_CUSTOM_PATH"] = "/opt/noc_custom"
        if self.is_pooled:
            if not self._pool:
                msg = f"Cannot use pooled service {self.name} without pool"
                raise ValueError(msg)
            r["NOC_POOL"] = self._pool
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
        if not _prepared_flags.may_process_config():
            return  # Already configured from other subclass
        # Build default config
        cfg = {
            "installation_name": config.noc.installation_name,
            "clickhouse": {"ro_user": "default"},
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

    def get_compose_volumes_config(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """Generate crashinfo and backup volume."""
        if not _prepared_flags.may_process_volumes():
            return None  # Already prepared from other subclass
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

    def get_compose_extra(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        """Set caps."""
        r = super().get_compose_extra(config, svc) or {}
        if (
            self.is_pooled
            and self.require_pool_network
            and self._pool
            and config.pools[self._pool].address.gw
        ):
            cap_add = r.get("cap_add", [])
            if "NET_ADMIN" not in cap_add:
                cap_add.append("NET_ADMIN")
            r["cap_add"] = cap_add
        return r if r else None


class NocHcService(NocService):
    """Noc service with healthcheck."""

    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD-SHELL", "curl http://$$HOSTNAME:1200/health"],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }


class _PreparedFlags(object):
    """Global state to perform configuration only once."""

    def __init__(self) -> None:
        self._config: bool = True
        self._volumes: bool = True

    def may_process_config(self) -> bool:
        """Check if config should be processed."""
        v = self._config
        self._config = False
        return v

    def may_process_volumes(self) -> bool:
        """Check if config should be processed."""
        v = self._volumes
        self._volumes = False
        return v


_prepared_flags = _PreparedFlags()

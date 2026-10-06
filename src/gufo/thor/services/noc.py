# ---------------------------------------------------------------------
# Gufo Thor: noc service
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""NocService base class."""

# Python Modules
from pathlib import Path
from typing import Any

# Third-party modules
import yaml

# Gufo Thor modules
from ..artefact import Artefact
from ..config import ServiceConfig, config
from ..images import get_image
from ..utils import ensure_directory, merge_dict
from .base import BaseService, ComposeDependsCondition, Role

noc_settings = Artefact("settings", Path("etc", "noc", "settings.yml"))


class NocService(BaseService):
    """Basic class for all NOC's services."""

    is_noc = True
    name = "noc"
    role = Role.APP
    compose_environment = {
        "NOC_CONFIG": "yaml:///etc/noc/settings.yml,env:///NOC",
        "NOC_LISTEN": "eth0:1200",  # eth0 is always `noc` network
    }
    compose_configs = [
        noc_settings.at(Path("/", "etc", "noc", "settings.yml"))
    ]

    def get_compose_image(self, svc: ServiceConfig | None = None) -> str:
        """Get docker-compose.yml `image` section.

        Use a service-specific or global NOC tag when configured.

        Args:
            svc: Service's config from `services` part, if any.

        Returns:
            Image name.
        """
        image = get_image("noc")
        tag = svc.tag if svc and svc.tag else config.noc.tag
        if tag:
            image = f"{image.rsplit(':', 1)[0]}:{tag}"
        return image

    def get_compose_command(
        self, svc: ServiceConfig | None = None
    ) -> str | None:
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
        self, svc: ServiceConfig | None = None
    ) -> list[str] | None:
        """
        Get volumes section.

        Mount repo and custom when necessary.
        """
        # Config + crashinfo
        r: list[str] = ["crashinfo:/var/lib/noc/cp/crashinfo/new"]
        # Mount NOC repo inside an image
        if config.noc.path:
            r.append(f"{config.noc.path}:/opt/noc:cached")
        # Mount custom inside an image
        if config.noc.custom:
            r.append(f"{config.noc.custom}:/opt/noc_custom:cached")
        return r if r else None

    def get_compose_environment(
        self, svc: ServiceConfig | None = None
    ) -> dict[str, str] | None:
        """Get environment section."""
        r: dict[str, str] = super().get_compose_environment(svc) or {}
        if self.is_pooled:
            if not self._pool:
                raise ValueError(
                    f"Cannot use pooled service {self.name} without pool"
                )
            r["NOC_POOL"] = self._pool
        return r if r else None

    def prepare_compose_config(
        self,
        svc: ServiceConfig | None = None,
        *,
        services: list["BaseService"],
    ) -> None:
        """
        Render configuration files.

        NB: As the NocServices is the base class for a bunch of services,
        ensure, the configuration files are rendered only once.
        """
        if not _prepared_flags.may_process_config():
            return  # Already configured from other subclass
        # Write
        cfg = self.get_noc_settings()
        noc_settings.write(yaml.dump(cfg))
        # Ensure directories
        ensure_directory(Path("data", "crashinfo"))
        ensure_directory(config.local_backup_path)

    def get_noc_settings(self) -> dict[str, Any]:
        """
        Get data for settings.yml.

        Returns:
            Data which can be serialized to settings.yml.
        """
        # Build default config
        cfg: dict[str, Any] = {
            "installation_name": config.noc.installation_name,
            "clickhouse": {"ro_user": "default"},
            "language": config.noc.language,
            "pg": {
                "db": "noc",
                "user": "noc",
            },
            "web": {
                "theme": config.noc.theme,
            },
            "msgstream": {
                "client_class": "noc.core.msgstream.kafka.KafkaClient",
            },
            "kafka": {"addresses": "kafka:9092"},
        }
        # Apply user config
        if config.noc.config:
            cfg = merge_dict(cfg, config.noc.config)
        # Apply custom if necessary
        if config.noc.custom:
            cfg.setdefault("path", {})["custom_path"] = "/opt/noc_custom"
        return cfg

    def get_compose_volumes_config(
        self, svc: ServiceConfig | None = None
    ) -> dict[str, dict[str, Any]] | None:
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
                    "device": f"./{config.local_backup_path}",
                    "o": "bind",
                },
            },
        }

    def get_compose_extra(
        self, svc: ServiceConfig | None = None
    ) -> dict[str, Any] | None:
        """Set caps."""
        r = super().get_compose_extra(svc) or {}
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


class _PreparedFlags:
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

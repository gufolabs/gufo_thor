# ---------------------------------------------------------------------
# Gufo Thor: VyOS 1.5 lab router
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""VyOS lab router."""

# Python modules
from pathlib import Path
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, LabConfig, LabNodeConfig
from .base import BaseLab, DockerConsoleArgs


class VyOS15Lab(BaseLab):
    """VyOS lab router."""

    name = "vyos15"
    image = "ghcr.io/gufolabs/vyos15"
    default_version = "latest"

    def get_compose_volumes(
        self, config: Config, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> List[str]:
        """Generate volumes settings."""
        conf_root = self.get_config_dir(lab_config, node_config)
        conf_path = conf_root / "config.boot"
        if not conf_path.exists():
            self._write_initial_config(
                conf_path, config, lab_config, node_config
            )
        return [f"./{conf_root}:/opt/vyatta/etc/config"]

    def _write_initial_config(
        self,
        conf_path: Path,
        config: Config,
        lab_config: LabConfig,
        node_config: LabNodeConfig,
    ) -> None:
        ctx = self.get_config_context(config, lab_config, node_config)
        self.render_file(conf_path, "config.boot.j2", **ctx)

    def get_docker_console_args(
        self, config: Config, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> Optional[DockerConsoleArgs]:
        """Get effective docker console args."""
        user = node_config.users[0].user if node_config.users else "vyos"
        return DockerConsoleArgs(args=["-u", user], argv=["/bin/vbash"])

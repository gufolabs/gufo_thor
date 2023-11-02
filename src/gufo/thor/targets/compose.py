# ---------------------------------------------------------------------
# Gufo Thor: ComposeTarget
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""docker compose target."""

# Python modules
import os
from pathlib import Path
from typing import Any, Dict

# Third-party mofules
import yaml

# Gufo Thor modules
from ..log import logger
from ..services.base import BaseService, loader
from .base import BaseTarget


class ComposeTarget(BaseTarget):
    """
    docker compose target.

    Prepares `docker-compose.yml` and all the configuration,
    then starts with `docker compose up -d`
    """

    name = "compose"

    def prepare(self: "ComposeTarget") -> None:
        """Generate docker-compose.yml, data directories, and configs."""
        # Generate docker-compose.yml
        dc = self.render_config()
        path = "docker-compose.yml"
        logger.info("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(dc)
        # Generate directories and config
        for svc in BaseService.resolve(self.config.services):
            logger.info("Configuring service %s", svc.name)
            # Create configuration directories, if necessary
            etc_dirs = svc.get_compose_etc_dirs(
                self.config, self.config.services.get(svc.name)
            )
            if etc_dirs:
                prefix = Path("etc")
                self._ensure_directory(prefix)
                for d in etc_dirs:
                    self._ensure_directory(prefix / d)
            # Create data directories, if necessary
            data_dirs = svc.get_compose_data_dirs(
                self.config, self.config.services.get(svc.name)
            )
            if data_dirs:
                prefix = Path("data")
                self._ensure_directory(prefix)
                for d in data_dirs:
                    self._ensure_directory(prefix / d)
            # Create config
            svc.prepare_compose_config(
                self.config, self.config.services.get(svc.name)
            )

    @staticmethod
    def _ensure_directory(path: Path) -> None:
        """
        Check directory is exists and create, if necessary.

        Args:
            path: Directory path.
        """
        if os.path.exists(path):
            logger.info("Directory %s is already exists. Skipping", path)
            return
        logger.info("Creating directory %s", path)
        os.makedirs(path)

    def render_config(self: "ComposeTarget") -> str:
        """
        Render `docker-compose.yml`.

        Returns:
            String containing config.
        """
        s: str = yaml.safe_dump(self._get_config_dict(), sort_keys=False)
        return s

    def _get_config_dict(self: "ComposeTarget") -> Dict[str, Any]:
        """Get dict of docker-compose.yml."""
        return {
            "version": "3",
            "services": self._get_services_config(),
            "networks": {
                "noc": {
                    "driver": "bridge",
                    "ipam": {
                        "config": [
                            {
                                "subnet": "172.20.0.0/24",
                                "gateway": "172.20.0.1",
                            }
                        ]
                    },
                }
            },
        }

    def _get_services_config(self: "ComposeTarget") -> Dict[str, Any]:
        """Builf services section of config."""
        # Check for invalid services
        invalid = {
            svc for svc in self.config.services if not loader[svc].is_noc
        }
        if invalid:
            msg = f"Invalid services: {', '.join(invalid)}"
            raise ValueError(msg)
        # Resolve services
        return {
            svc.name: svc.get_compose_config(
                self.config, self.config.services.get(svc.name)
            )
            for svc in BaseService.resolve(self.config.services)
        }

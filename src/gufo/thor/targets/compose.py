# ---------------------------------------------------------------------
# Gufo Thor: ComposeTarget
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""docker compose target."""

# Python modules
import os
from typing import Any, Dict

# Third-party mofules
import yaml

# Gufo Thor modules
from ..log import logger
from ..services.base import BaseService, loader
from .base import BaseTarget


class ComposeTarget(BaseTarget):
    name = "compose"

    def prepare(self: "ComposeTarget") -> None:
        # Generate docker-compose.yml
        dc = self.render_config()
        path = "docker-compose.yml"
        logger.info("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(dc)
        # Generate directories and config
        for svc in BaseService.resolve(self.config.services):
            logger.info("Configuring service %s", svc.name)
            # Create directories
            dirs = svc.get_compose_dirs(
                self.config, self.config.services.get(svc.name)
            )
            if dirs is not None:
                for d in dirs:
                    if os.path.exists(d):
                        logger.info(
                            "Directory %s is already exists. Skipping", d
                        )
                    else:
                        logger.info("Creating directory %s", d)
                        os.makedirs(d)
            # Create config
            svc.prepare_compose_config(
                self.config, self.config.services.get(svc.name)
            )

    def render_config(self: "ComposeTarget") -> str:
        return yaml.safe_dump(self._get_config_dict(), sort_keys=False)

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

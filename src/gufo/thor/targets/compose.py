# ---------------------------------------------------------------------
# Gufo Thor: ComposeTarget
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""docker compose target."""

# Python modules
import json
from pathlib import Path
from typing import Any, Dict, List

# Third-party mofules
import yaml

# Gufo Thor modules
from ..services.base import BaseService, loader
from ..utils import ensure_directory, write_file
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
        write_file(Path("docker-compose.yml"), self.render_config())
        # Generate .env
        env_data: List[str] = []
        if self.config.project is not None:
            env_data.append(f"COMPOSE_PROJECT_NAME={self.config.project}")
        write_file(Path(".env"), "\n".join(env_data))
        # Create etc/
        etc = Path("etc")
        ensure_directory(etc)
        # Generate directories and configs
        slots: Dict[str, int] = {}
        for svc in BaseService.resolve(self.config.services):
            svc_cfg = self.config.services.get(svc.name)
            # Process slots
            if svc.require_slots:
                slots[svc.name] = svc_cfg.scale if svc_cfg else 1
            # Create config
            svc.prepare_compose_config(self.config, svc_cfg)
            # Service discovery
            sd = svc.get_service_discovery(self.config, svc_cfg)
            if sd:
                self._configure_service_discovery(svc.name, sd)
        # Save slots
        write_file(
            etc / "slots.cfg",
            "\n".join(f"{k}: {v}" for k, v in sorted(slots.items())),
        )

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
        r = {
            "version": "3.3",
            "services": self._get_services_config(),
            "networks": {
                "noc": {
                    "driver": "bridge",
                }
            },
        }
        # Configure volumes
        volumes: Dict[str, Dict[str, Any]] = {}
        for svc in BaseService.resolve(self.config.services):
            vc = svc.get_compose_volumes_config(
                self.config, self.config.services.get(svc.name)
            )
            if not vc:
                continue
            for n, c in vc.items():
                if n in volumes:
                    volumes[n].update(c)
                else:
                    volumes[n] = c
        if volumes:
            r["volumes"] = volumes
        return r

    def _get_services_config(self: "ComposeTarget") -> Dict[str, Any]:
        """Build services section of config."""
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

    def _configure_service_discovery(
        self: "ComposeTarget", name: str, sd: Dict[str, int]
    ) -> None:
        """Prepare service discovery config."""
        sd_root = Path("etc", "consul")
        ensure_directory(sd_root)
        for svc_name, port in sd.items():
            path = sd_root / f"{svc_name}-{port}.json"
            cfg = {
                "service": {
                    "name": svc_name,
                    "address": name,
                    "port": port,
                    "checks": [
                        {
                            "id": f"tcp-{svc_name}-{port}",
                            "interval": "1s",
                            "tcp": f"{name}:{port}",
                            "timeout": "1s",
                        }
                    ],
                }
            }
            write_file(path, json.dumps(cfg))

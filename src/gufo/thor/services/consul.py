# ---------------------------------------------------------------------
# Gufo Thor: consul service
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""
consul service.

Attributes:
    consul: consul service singleton.
"""

# Python modules
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from gufo.thor.config import Config, ServiceConfig

# Gufo Thor modules
from ..artefact import Artefact
from .base import BaseService, ComposeDependsCondition


class ConsulService(BaseService):
    """consul service."""

    name = "consul"
    compose_image = "consul:1.15"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": [
            "CMD",
            "curl",
            "--fail",
            "http://localhost:8500/v1/status/leader",
        ],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }
    compose_volumes = [
        "consul_data:/consul/data",
    ]
    compose_volumes_config = {"consul_data": {}}

    def __init__(self) -> None:
        super().__init__()
        self.discovered_services: List[Artefact] = []

    def get_compose_configs(
        self, config: Config, svc: Optional["ServiceConfig"]
    ) -> Optional[List[Artefact]]:
        """Add configs for discovered services."""
        r = super().get_compose_configs(config, svc) or []
        r += self.discovered_services
        return r or None

    def register_service(self, name: str, port: int) -> None:
        """
        Add discovered service.

        Args:
            name: Service name.
            port: Service port.
        """
        cfg: Dict[str, Any] = {
            "service": {
                "name": name,
                "address": name,
                "port": port,
                "checks": [
                    {
                        "id": f"tcp-{name}-{port}",
                        "interval": "1s",
                        "tcp": f"{name}:{port}",
                        "timeout": "1s",
                    }
                ],
            }
        }
        file_name = f"{name}-{port}.json"
        art = Artefact(
            f"consul-svc-{name}-{port}",
            Path("etc", "consul", file_name),
        )
        art.write(json.dumps(cfg))
        self.discovered_services.append(
            art.at(Path("/", "consul", "config", file_name))
        )


consul = ConsulService()

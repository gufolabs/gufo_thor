# ---------------------------------------------------------------------
# Gufo Thor: liftbridge service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
liftbridge service.

Attributes:
    liftbridge: liftbridge service singleton.
"""

# Python modules
from pathlib import Path
from typing import Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService


class LiftbridgeService(BaseService):
    """liftbridge service."""

    name = "liftbridge"
    compose_image = "liftbridge/liftbridge:v1.9.0"
    compose_entrypoint = "liftbridge --config /etc/liftbridge.yml"
    compose_volumes = [
        "./data/liftbridge:/data/",
        "./etc/liftbridge.yml:/etc/liftbridge.yml",
    ]
    compose_data_dirs = [Path("liftbridge")]
    service_discovery = {"liftbridge": 9292}

    def prepare_compose_config(
        self: "LiftbridgeService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        """Generate config."""
        self.render_file(Path("etc", "liftbridge.yml"), "liftbridge.yml")


liftbridge = LiftbridgeService()

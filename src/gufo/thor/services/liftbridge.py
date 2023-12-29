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
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService


class LiftbridgeService(BaseService):
    """liftbridge service."""

    name = "liftbridge"
    compose_image = "liftbridge/liftbridge:v1.9.0"
    compose_entrypoint = "liftbridge --config /etc/liftbridge.yml"
    compose_volumes = [
        "./etc/liftbridge.yml:/etc/liftbridge.yml:ro",
        "liftbridge_data:/data/",
    ]
    compose_volumes_config = {"liftbridge_data": {}}
    service_discovery = {"liftbridge": 9292}
    compose_extra = {"user": "root"}

    def prepare_compose_config(
        self: "LiftbridgeService",
        config: Config,
        svc: Optional[ServiceConfig],
        services: List["BaseService"],
    ) -> None:
        """Generate config."""
        self.render_file(Path("etc", "liftbridge.yml"), "liftbridge.yml")


liftbridge = LiftbridgeService()

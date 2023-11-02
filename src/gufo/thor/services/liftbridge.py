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
from .registrator import registrator


class LiftbridgeService(BaseService):
    """liftbridge service."""

    name = "liftbridge"
    dependencies = (registrator,)
    compose_image = "liftbridge/liftbridge:v1.9.0"
    compose_entrypoint = "liftbridge --config /etc/liftbridge.yml"
    compose_volumes = [
        "./data/liftbridge:/data/",
        "./etc/liftbridge.yml:/etc/liftbridge.yml",
    ]
    compose_environment = {
        "SERVICE_9292_NAME": "liftbridge",
    }

    def get_compose_dirs(
        self: "LiftbridgeService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> Optional[List[str]]:
        """Request data directories to be createed."""
        return ["etc", "data/liftbridge"]

    def prepare_compose_config(
        self: "LiftbridgeService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        """Generate config."""
        self.render_file(Path("etc", "liftbridge.yml"), "liftbridge.yml")


liftbridge = LiftbridgeService()

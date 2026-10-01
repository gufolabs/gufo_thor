# ---------------------------------------------------------------------
# Gufo Thor: BaseTarget
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
BaseTarget definitions.

Attributes:
    loader: Target loader.
"""

# Python modules
from abc import ABC
from typing import Type

# Gufo Labs modules
from gufo.loader import Loader

# Gufo Thor modules
from ..config import config
from ..services.base import BaseService


class BaseTarget(ABC):
    """
    Base class for deploy targets.

    Attributes:
        name: Target name.
        services: Resolved services configured for this target.
    """

    name: str

    def __init__(self) -> None:
        """Initialize the target before loading its configuration."""
        self.services: list[BaseService] = []

    def prepare(self) -> None:
        """Load configuration and resolve configured services."""
        config.setup()
        self.services = list(BaseService.resolve(config.services))


loader = Loader[Type[BaseTarget]](base="gufo.thor.targets", exclude=("base",))

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
from abc import ABC, abstractmethod
from typing import Type

# Gufo Labs modules
from gufo.loader import Loader

# Gufo Thor modules
from ..config import Config


class BaseTarget(ABC):
    """
    Base class for deploy targets.

    Attributes:
        name: Target name.
    """

    name: str

    def __init__(self: "BaseTarget", config: Config) -> None:
        self.config = config

    @abstractmethod
    def prepare(self: "BaseTarget") -> None:
        """Prepare environment before start."""
        ...


loader = Loader[Type[BaseTarget]](base="gufo.thor.targets", exclude=("base",))

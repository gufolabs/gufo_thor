# ---------------------------------------------------------------------
# Gufo Thor: activator service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
activator service.

Attributes:
    activator: activator service singleton.
"""

# Gufo Thor modules
from .liftbridge import liftbridge
from .noc import NocService
from .sae import sae


class ActivatorService(NocService):
    """activator service."""

    name = "activator"
    dependencies = (sae, liftbridge)


activator = ActivatorService()

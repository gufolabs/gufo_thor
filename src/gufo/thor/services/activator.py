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
from .kafka import kafka
from .migrate import migrate
from .noc import NocService
from .sae import sae


class ActivatorService(NocService):
    """activator service."""

    name = "activator"
    dependencies = (kafka, migrate, sae)
    is_pooled = True
    require_pool_network = True


activator = ActivatorService()

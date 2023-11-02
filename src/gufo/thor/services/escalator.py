# ---------------------------------------------------------------------
# Gufo Thor: escalator service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
escalator service.

Attributes:
    escalator: escalator service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class EscalatorService(NocService):
    """escalator service."""

    name = "escalator"


escalator = EscalatorService()

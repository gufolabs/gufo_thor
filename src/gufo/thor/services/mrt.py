# ---------------------------------------------------------------------
# Gufo Thor: mrt service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
mrt service.

Attributes:
    mrt: mrt service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class MrtService(NocService):
    """mrt service."""

    name = "mrt"


mrt = MrtService()

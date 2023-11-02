# ---------------------------------------------------------------------
# Gufo Thor: mib service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
mib service.

Attributes:
    mib: mib service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class MibService(NocService):
    """mib service."""

    name = "mib"


mib = MibService()

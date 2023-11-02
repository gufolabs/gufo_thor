# ---------------------------------------------------------------------
# Gufo Thor: zeroconf service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
zeroconf service.

Attributes:
    zeroconf: zeroconf service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class ZeroconfService(NocService):
    """zeroconf service."""

    name = "zeroconf"


zeroconf = ZeroconfService()

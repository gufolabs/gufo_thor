# ---------------------------------------------------------------------
# Gufo Thor: bh service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
bh service.

Attributes:
    bh: bh service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class BhService(NocService):
    """bh service."""

    name = "bh"
    is_pooled = True
    require_pool_network = True


bh = BhService()

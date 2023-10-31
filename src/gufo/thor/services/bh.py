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
    name = "bh"


bh = BhService()

# ---------------------------------------------------------------------
# Gufo Thor: nbi service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
nbi service.

Attributes:
    nbi: nbi service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class NbiService(NocService):
    name = "nbi"


nbi = NbiService()

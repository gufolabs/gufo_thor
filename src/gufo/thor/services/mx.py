# ---------------------------------------------------------------------
# Gufo Thor: mx service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
mx service.

Attributes:
    mx: mx service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class MxService(NocService):
    name = "mx"


mx = MxService()

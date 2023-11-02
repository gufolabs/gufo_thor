# ---------------------------------------------------------------------
# Gufo Thor: sae service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
sae service.

Attributes:
    sae: sae service singleton.
"""

# Gufo Thor modules
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class SaeService(NocService):
    """sae service."""

    name = "sae"
    dependencies = (migrate, postgres, mongo)


sae = SaeService()

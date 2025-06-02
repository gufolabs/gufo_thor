# ---------------------------------------------------------------------
# Gufo Thor: correlator service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
correlator service.

Attributes:
    correlator: correlator service singleton.
"""

# Gufo Thor modules
from .kafka import kafka
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class CorrelatorService(NocService):
    """correlator service."""

    name = "correlator"
    dependencies = (kafka, migrate, mongo, postgres)
    is_pooled = True
    require_slots = True


correlator = CorrelatorService()

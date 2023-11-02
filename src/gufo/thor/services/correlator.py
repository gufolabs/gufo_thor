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
from .liftbridge import liftbridge
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class CorrelatorService(NocService):
    """correlator service."""

    name = "correlator"
    dependencies = (migrate, postgres, mongo, liftbridge)


correlator = CorrelatorService()

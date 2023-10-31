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
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class CorrelatorService(NocService):
    name = "correlator"
    dependencies = (postgres, mongo, liftbridge)


correlator = CorrelatorService()

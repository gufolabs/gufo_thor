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
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class NbiService(NocService):
    name = "nbi"
    dependencies = (migrate, mongo, postgres)


nbi = NbiService()

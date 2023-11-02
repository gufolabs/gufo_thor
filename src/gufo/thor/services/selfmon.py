# ---------------------------------------------------------------------
# Gufo Thor: selfmon service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
selfmon service.

Attributes:
    selfmon: selfmon service singleton.
"""

# Gufo Thor modules
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class SelfmonService(NocService):
    """selfmon service."""

    name = "selfmon"
    dependencies = (migrate, postgres, mongo)


selfmon = SelfmonService()

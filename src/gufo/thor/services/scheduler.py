# ---------------------------------------------------------------------
# Gufo Thor: scheduler service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
scheduler service.

Attributes:
    scheduler: scheduler service singleton.
"""

# Gufo Thor modules
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class SchedulerService(NocService):
    """scheduler service."""

    name = "scheduler"
    dependencies = (migrate, postgres, mongo)


scheduler = SchedulerService()

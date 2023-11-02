# ---------------------------------------------------------------------
# Gufo Thor: worker service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
worker service.

Attributes:
    worker: worker service singleton.
"""

# Gufo Thor modules
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class WorkerService(NocService):
    """worker service."""

    name = "worker"
    dependencies = (migrate, postgres, mongo)


worker = WorkerService()

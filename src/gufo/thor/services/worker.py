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
from .datastream import datastream
from .kafka import kafka
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class WorkerService(NocService):
    """worker service."""

    name = "worker"
    dependencies = (datastream, kafka, migrate, mongo, postgres)
    allow_scale = True
    require_slots = True


worker = WorkerService()

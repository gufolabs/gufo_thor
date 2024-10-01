# ---------------------------------------------------------------------
# Gufo Thor: worker service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
worker service.

Attributes:
    runner: runner service singleton.
"""

# Gufo Thor modules
from .kafka import kafka
from .migrate import migrate
from .mongo import mongo
from .noc import NocService


class RunnerService(NocService):
    """runner service."""

    name = "runner"
    dependencies = (kafka, migrate, mongo)
    allow_scale = False
    require_slots = False


runner = RunnerService()

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
from .noc import NocService


class SchedulerService(NocService):
    name = "scheduler"


scheduler = SchedulerService()

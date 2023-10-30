# ---------------------------------------------------------------------
# Gufo Thor: scheduler service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class SchedulerService(NocService):
    name = "scheduler"


scheduler = SchedulerService()

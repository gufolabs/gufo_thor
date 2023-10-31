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
from .noc import NocService


class WorkerService(NocService):
    name = "worker"


worker = WorkerService()

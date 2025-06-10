# ---------------------------------------------------------------------
# Gufo Thor: metrics service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
metrics service.

Attributes:
    metrics: metrics service singleton.
"""

# Gufo Thor modules
from .chwriter import chwriter
from .kafka import kafka
from .migrate import migrate
from .noc import NocService


class MetricsService(NocService):
    """metrics service."""

    name = "metrics"
    require_slots = True
    dependencies = (chwriter, kafka, migrate)


metrics = MetricsService()

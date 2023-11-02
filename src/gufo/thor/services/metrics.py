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
from .noc import NocService


class MetricsService(NocService):
    """metrics service."""

    name = "metrics"


metrics = MetricsService()

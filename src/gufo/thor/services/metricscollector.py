# ---------------------------------------------------------------------
# Gufo Thor: metricscollector service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
metricscollector service.

Attributes:
    metricscollector: metricscollector service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class MetricscollectorService(NocService):
    """metricscollector service."""

    name = "metricscollector"


metricscollector = MetricscollectorService()

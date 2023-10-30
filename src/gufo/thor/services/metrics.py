# ---------------------------------------------------------------------
# Gufo Thor: metrics service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class MetricsService(NocService):
    name = "metrics"


metrics = MetricsService()

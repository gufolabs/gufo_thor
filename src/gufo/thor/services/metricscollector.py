# ---------------------------------------------------------------------
# Gufo Thor: metricscollector service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class MetricscollectorService(NocService):
    name = "metricscollector"


metricscollector = MetricscollectorService()

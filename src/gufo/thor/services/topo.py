# ---------------------------------------------------------------------
# Gufo Thor: topo service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
topo service.

Attributes:
    topo: topo service singleton.
"""

# Gufo Thor modules
from .datastream import datastream
from .kafka import kafka
from .migrate import migrate
from .noc import NocService


class TopoService(NocService):
    """topo service."""

    name = "topo"
    dependencies = (datastream, kafka, migrate)


topo = TopoService()

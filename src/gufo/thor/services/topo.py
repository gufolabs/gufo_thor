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
from .noc import NocService


class TopoService(NocService):
    name = "topo"


topo = TopoService()

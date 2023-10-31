# ---------------------------------------------------------------------
# Gufo Thor: trapcollector service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
trapcollector service.

Attributes:
    trapcollector: trapcollector service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class TrapcollectorService(NocService):
    name = "trapcollector"


trapcollector = TrapcollectorService()

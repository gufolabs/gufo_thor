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
from .datastream import datastream
from .liftbridge import liftbridge
from .noc import NocService


class TrapcollectorService(NocService):
    """trapcollector service."""

    name = "trapcollector"
    dependencies = (datastream, liftbridge)


trapcollector = TrapcollectorService()

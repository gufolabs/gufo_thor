# ---------------------------------------------------------------------
# Gufo Thor: discovery service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
discovery service.

Attributes:
    discovery: discovery service singleton.
"""

# Gufo Thor modules
from .activator import activator
from .chwriter import chwriter
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class DiscoveryService(NocService):
    """discovery service."""

    name = "discovery"
    dependencies = (activator, chwriter, migrate, mongo, postgres)


discovery = DiscoveryService()

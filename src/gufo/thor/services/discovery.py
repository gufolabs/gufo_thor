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
from .clickhouse import clickhouse
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class DiscoveryService(NocService):
    """discovery service."""

    name = "discovery"
    dependencies = (migrate, postgres, mongo, clickhouse, activator)


discovery = DiscoveryService()

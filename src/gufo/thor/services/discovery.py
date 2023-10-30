# ---------------------------------------------------------------------
# Gufo Thor: discovery service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .activator import activator
from .clickhouse import clickhouse
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class DiscoveryService(NocService):
    name = "discovery"
    dependencies = (postgres, mongo, clickhouse, activator)


discovery = DiscoveryService()

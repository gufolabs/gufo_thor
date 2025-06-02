# ---------------------------------------------------------------------
# Gufo Thor: ping service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
ping service.

Attributes:
    ping: ping service singleton.
"""

# Gufo Thor modules
from .datastream import datastream
from .kafka import kafka
from .migrate import migrate
from .noc import NocService


class PingService(NocService):
    """ping service."""

    name = "ping"
    dependencies = (datastream, kafka, migrate)
    compose_extra = {
        "cap_add": [
            "NET_RAW",
        ],
    }
    is_pooled = True
    require_pool_network = True
    require_slots = True


ping = PingService()

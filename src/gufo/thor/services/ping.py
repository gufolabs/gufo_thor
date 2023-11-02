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
from .liftbridge import liftbridge
from .noc import NocService


class PingService(NocService):
    """ping service."""

    name = "ping"
    dependencies = (liftbridge, datastream)
    compose_extra = {
        "cap_add": [
            "SYS_NET_RAW",
        ],
    }


ping = PingService()

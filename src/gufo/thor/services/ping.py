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
    name = "ping"
    dependencies = (liftbridge, datastream)


ping = PingService()

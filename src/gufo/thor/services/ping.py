# ---------------------------------------------------------------------
# Gufo Thor: ping service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class PingService(NocService):
    name = "ping"


ping = PingService()

# ---------------------------------------------------------------------
# Gufo Thor: zeroconf service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class ZeroconfService(NocService):
    name = "zeroconf"


zeroconf = ZeroconfService()

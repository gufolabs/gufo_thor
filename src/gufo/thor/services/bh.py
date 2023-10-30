# ---------------------------------------------------------------------
# Gufo Thor: bh service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class BhService(NocService):
    name = "bh"


bh = BhService()

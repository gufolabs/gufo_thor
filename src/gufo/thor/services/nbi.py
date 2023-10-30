# ---------------------------------------------------------------------
# Gufo Thor: nbi service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class NbiService(NocService):
    name = "nbi"


nbi = NbiService()

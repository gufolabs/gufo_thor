# ---------------------------------------------------------------------
# Gufo Thor: mib service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class MibService(NocService):
    name = "mib"


mib = MibService()

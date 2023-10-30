# ---------------------------------------------------------------------
# Gufo Thor: escalator service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class EscalatorService(NocService):
    name = "escalator"


escalator = EscalatorService()

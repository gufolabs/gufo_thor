# ---------------------------------------------------------------------
# Gufo Thor: mrt service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class MrtService(NocService):
    name = "mrt"


mrt = MrtService()

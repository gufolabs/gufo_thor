# ---------------------------------------------------------------------
# Gufo Thor: tgsender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class TgsenderService(NocService):
    name = "tgsender"


tgsender = TgsenderService()

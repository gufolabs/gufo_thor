# ---------------------------------------------------------------------
# Gufo Thor: icqsender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class IcqsenderService(NocService):
    name = "icqsender"


icqsender = IcqsenderService()

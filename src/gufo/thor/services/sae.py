# ---------------------------------------------------------------------
# Gufo Thor: sae service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class SaeService(NocService):
    name = "sae"
    dependencies = (postgres, mongo)


sae = SaeService()

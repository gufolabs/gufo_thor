# ---------------------------------------------------------------------
# Gufo Thor: kafkasender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class KafkasenderService(NocService):
    name = "kafkasender"


kafkasender = KafkasenderService()

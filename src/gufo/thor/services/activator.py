# ---------------------------------------------------------------------
# Gufo Thor: activator service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .liftbridge import liftbridge
from .noc import NocService
from .sae import sae


class ActivatorService(NocService):
    name = "activator"
    dependencies = (sae, liftbridge)


activator = ActivatorService()

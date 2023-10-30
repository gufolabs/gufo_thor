# ---------------------------------------------------------------------
# Gufo Thor: ui service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class UiService(NocService):
    name = "ui"


ui = UiService()

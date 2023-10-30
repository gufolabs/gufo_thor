# ---------------------------------------------------------------------
# Gufo Thor: grafanads service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class GrafanadsService(NocService):
    name = "grafanads"


grafanads = GrafanadsService()

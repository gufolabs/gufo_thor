# ---------------------------------------------------------------------
# Gufo Thor: ui service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
ui service.

Attributes:
    ui: ui service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class UiService(NocService):
    name = "ui"


ui = UiService()

# ---------------------------------------------------------------------
# Gufo Thor: grafanads service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
grafanads service.

Attributes:
    grafanads: grafanads service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class GrafanadsService(NocService):
    """grafanads service."""

    name = "grafanads"


grafanads = GrafanadsService()

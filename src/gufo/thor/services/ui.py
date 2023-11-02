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
from .migrate import migrate
from .mongo import mongo
from .nginx import nginx
from .noc import NocService
from .postgres import postgres
from .traefik import traefik


class UiService(NocService):
    """ui service."""

    name = "ui"
    dependencies = (migrate, postgres, mongo, traefik, nginx)


ui = UiService()

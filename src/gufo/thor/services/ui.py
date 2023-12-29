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
from .auth import auth
from .envoy import envoy
from .login import login
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres
from .static import static


class UiService(NocService):
    """ui service."""

    name = "ui"
    dependencies = (auth, envoy, login, migrate, mongo, postgres, static)
    expose_http_prefix = "/api/ui/"


ui = UiService()

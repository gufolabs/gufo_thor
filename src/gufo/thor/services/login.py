# ---------------------------------------------------------------------
# Gufo Thor: login service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
login service.

Attributes:
    login: login service singleton.
"""

# Gufo Thor modules
from ..secret import secret_key
from .envoy import envoy
from .migrate import migrate
from .mongo import mongo
from .noc import NocHcService
from .postgres import postgres
from .static import static


class LoginService(NocHcService):
    """login service."""

    name = "login"
    dependencies = (envoy, migrate, mongo, postgres, static)
    allow_scale = True
    expose_http_prefix = "/api/login/"
    compose_secrets = [secret_key]


login = LoginService()

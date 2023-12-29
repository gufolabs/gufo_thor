# ---------------------------------------------------------------------
# Gufo Thor: login service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
login service.

Attributes:
    auth: auth service singleton.
"""

# Gufo Thor modules
from .envoy import envoy
from .liftbridge import liftbridge
from .migrate import migrate
from .mongo import mongo
from .noc import NocHcService


class AuthService(NocHcService):
    """auth service."""

    name = "auth"
    dependencies = (envoy, liftbridge, migrate, mongo)
    allow_scale = True
    expose_http_prefix = "/api/auth/"
    compose_command = (
        "/usr/local/bin/python3 /opt/noc/services/login/service.py"
    )


auth = AuthService()

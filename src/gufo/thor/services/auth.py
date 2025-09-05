# ---------------------------------------------------------------------
# Gufo Thor: auth service
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""
login service.

Attributes:
    auth: auth service singleton.
"""

# Gufo Thor modules
from ..secret import secret_key
from .envoy import envoy
from .kafka import kafka
from .migrate import migrate
from .mongo import mongo
from .noc import NocHcService


class AuthService(NocHcService):
    """auth service."""

    name = "auth"
    dependencies = (envoy, kafka, migrate, mongo)
    allow_scale = True
    expose_http_prefix = "/api/auth/"
    compose_command = (
        "/usr/local/bin/python3 /opt/noc/services/login/service.py"
    )
    compose_secrets = [secret_key]


auth = AuthService()

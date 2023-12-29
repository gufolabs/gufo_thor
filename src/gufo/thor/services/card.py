# ---------------------------------------------------------------------
# Gufo Thor: card service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
card service definition.

Attributes:
    card: card service singleton.
"""

# Gufo Thor modules
from .auth import auth
from .clickhouse import clickhouse
from .envoy import envoy
from .login import login
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres
from .static import static


class CardService(NocService):
    """card service."""

    name = "card"
    dependencies = (
        auth,
        clickhouse,
        envoy,
        login,
        migrate,
        mongo,
        postgres,
        static,
    )
    expose_http_prefix = "/api/card/"
    require_http_auth = True


card = CardService()

# ---------------------------------------------------------------------
# Gufo Thor: bi service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
bi service.

Attributes:
    bi: bi service singleton.
"""

# Gufo Thor modules
from .auth import auth
from .clickhouse import clickhouse
from .envoy import envoy
from .login import login
from .migrate import migrate
from .noc import NocService
from .static import static


class BiService(NocService):
    """bi service."""

    name = "bi"
    dependencies = (auth, clickhouse, envoy, login, migrate, static)
    expose_http_prefix = "/api/bi/"


bi = BiService()

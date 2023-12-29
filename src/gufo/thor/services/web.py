# ---------------------------------------------------------------------
# Gufo Thor: web service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
web service.

Attributes:
    web: web service singleton.
"""

# Gufo Thor modules
from .auth import auth
from .clickhouse import clickhouse
from .envoy import envoy
from .login import login
from .migrate import migrate
from .mongo import mongo
from .noc import NocHcService
from .postgres import postgres
from .static import static
from .worker import worker


class WebService(NocHcService):
    """web service."""

    name = "web"
    dependencies = (
        auth,
        clickhouse,
        envoy,
        login,
        migrate,
        mongo,
        postgres,
        static,
        worker,
    )
    allow_scale = True
    expose_http_prefix = "/"
    require_http_auth = True


web = WebService()

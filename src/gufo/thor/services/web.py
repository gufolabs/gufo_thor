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
from .clickhouse import clickhouse
from .migrate import migrate
from .mongo import mongo
from .nginx import nginx
from .noc import NocHcService
from .postgres import postgres
from .traefik import traefik
from .worker import worker


class WebService(NocHcService):
    """web service."""

    name = "web"
    dependencies = (
        migrate,
        postgres,
        mongo,
        clickhouse,
        traefik,
        nginx,
        worker,
    )
    allow_scale = True


web = WebService()

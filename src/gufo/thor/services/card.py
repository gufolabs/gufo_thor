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
from .clickhouse import clickhouse
from .migrate import migrate
from .mongo import mongo
from .nginx import nginx
from .noc import NocService
from .postgres import postgres
from .traefik import traefik


class CardService(NocService):
    """card service."""

    name = "card"
    dependencies = (migrate, postgres, mongo, clickhouse, traefik, nginx)


card = CardService()

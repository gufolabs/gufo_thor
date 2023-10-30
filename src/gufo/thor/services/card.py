# ---------------------------------------------------------------------
# Gufo Thor: card service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
CardService definition.

Attributes:
    card: CardService singleton.
"""

# Gufo Thor modules
from .clickhouse import clickhouse
from .mongo import mongo
from .nginx import nginx
from .noc import NocService
from .postgres import postgres
from .traefik import traefik


class CardService(NocService):
    """Card service."""

    name = "card"
    dependencies = (postgres, mongo, clickhouse, traefik, nginx)


card = CardService()

# ---------------------------------------------------------------------
# Gufo Thor: web service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .clickhouse import clickhouse
from .mongo import mongo
from .nginx import nginx
from .noc import NocService
from .postgres import postgres
from .traefik import traefik


class WebService(NocService):
    name = "web"
    dependencies = (postgres, mongo, clickhouse, traefik, nginx)


web = WebService()

# ---------------------------------------------------------------------
# Gufo Thor: datastream service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
datastream service.

Attributes:
    datastream: datastream service singleton.
"""

# Gufo Thor modules
from .mongo import mongo
from .noc import NocService
from .traefik import traefik


class DatastreamService(NocService):
    """datastream service."""

    name = "datastream"
    dependencies = (mongo, traefik)


datastream = DatastreamService()

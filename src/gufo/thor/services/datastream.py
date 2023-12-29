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
from .auth import auth
from .envoy import envoy
from .migrate import migrate
from .mongo import mongo
from .noc import NocService


class DatastreamService(NocService):
    """datastream service."""

    name = "datastream"
    dependencies = (auth, envoy, migrate, mongo)
    expose_http_prefix = "/api/datastream/"


datastream = DatastreamService()

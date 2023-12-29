# ---------------------------------------------------------------------
# Gufo Thor: nbi service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
nbi service.

Attributes:
    nbi: nbi service singleton.
"""

# Gufo Thor modules
from .auth import auth
from .envoy import envoy
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class NbiService(NocService):
    """nbi service."""

    name = "nbi"
    dependencies = (auth, envoy, migrate, mongo, postgres)
    expose_http_prefix = "/api/nbi/"


nbi = NbiService()

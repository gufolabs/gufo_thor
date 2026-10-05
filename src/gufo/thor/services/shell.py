# ---------------------------------------------------------------------
# Gufo Thor: shell service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
web service.

Attributes:
    shell: shell virtual service singleton.
"""

# Gufo Thor modules

from gufo.thor.config import ServiceConfig

from .clickhouse import clickhouse
from .mongo import mongo
from .noc import NocService
from .postgres import postgres
from .worker import worker


class ShellService(NocService):
    """web service."""

    name = "shell"
    dependencies = (clickhouse, mongo, postgres, worker)
    compose_extra = {"scale": 0}

    def get_compose_command(
        self: NocService, svc: ServiceConfig | None = None
    ) -> str | None:
        """Override to bash."""
        return "/bin/bash"


shell = ShellService()

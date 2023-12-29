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
from typing import Optional

from gufo.thor.config import Config, ServiceConfig

from .clickhouse import clickhouse
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres
from .worker import worker


class ShellService(NocService):
    """web service."""

    name = "shell"
    dependencies = (clickhouse, migrate, mongo, postgres, worker)
    compose_extra = {"scale": 0}

    def get_compose_command(
        self: NocService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        """Override to bash."""
        return "/bin/bash"


shell = ShellService()

# ---------------------------------------------------------------------
# Gufo Thor: migrate service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
migrate service.

Attributes:
    migrate: migrate service singleton.
"""

# Python modules

# Gufo Thor modules
from typing import Dict, List, Optional

from gufo.thor.config import Config, ServiceConfig

from .base import ComposeDependsCondition
from .clickhouse import clickhouse
from .consul import consul
from .liftbridge import liftbridge
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class MigrateService(NocService):
    """
    Database migrations.

    Migrate is a virtual service which launched just after
    database services became healthy. Then it applies
    pending database migrations and exits.
    Other database-dependend services are started only
    after successful termination of migrate.
    """

    name = "migrate"
    dependencies = (clickhouse, consul, liftbridge, mongo, postgres)
    compose_depends_condition = ComposeDependsCondition.COMPLETED_SUCCESSFULLY
    compose_command = "./scripts/deploy/migrate.sh"

    def get_compose_volumes(
        self: "MigrateService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """
        Get volumes settings for docker compose.

        Additionaly map slots configuration.
        """
        r = super().get_compose_volumes(config, svc) or []
        r.append("./etc/slots.cfg:/etc/slots.cfg:ro")
        return r

    def get_compose_environment(
        self: "MigrateService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        """
        Environment settings for container.

        Additionally set NOC_MIGRATE_SLOTS_PATH.
        """
        r = super().get_compose_environment(config, svc) or {}
        r["NOC_MIGRATE_SLOTS_PATH"] = "/etc/slots.cfg"
        return r


migrate = MigrateService()

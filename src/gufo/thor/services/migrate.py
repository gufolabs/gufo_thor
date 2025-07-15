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
from typing import Dict, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import ComposeDependsCondition, Role
from .clickhouse import clickhouse
from .consul import consul
from .kafka import kafka
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
    dependencies = (clickhouse, consul, kafka, mongo, postgres)
    compose_depends_condition = ComposeDependsCondition.COMPLETED_SUCCESSFULLY
    compose_command = "./scripts/deploy/migrate.sh"
    role = Role.UTILS

    def get_compose_command(
        self: "MigrateService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        """
        Get compose command.

        Considers config.cli.no_migrations option.
        """
        if config.noc.migrate:
            return self.compose_command
        return "/bin/true"

    def get_compose_environment(
        self: "MigrateService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        """
        Environment settings for container.

        Additionally set NOC_MIGRATE_SLOTS_PATH.
        """
        r = super().get_compose_environment(config, svc) or {}
        # Calculate pools
        for pool_name in config.pools:
            r[f"NOC_MIGRATE_POOL_{pool_name}"] = pool_name
        # Calculate slots
        for service in self.resolve(config.services):
            if service.require_slots:
                sn = service.get_compose_name()
                if sn in config.services:
                    scale = config.services[sn].scale
                else:
                    scale = 1
                r[f"NOC_MIGRATE_SLOTS_{sn.replace('-', '_')}"] = str(scale)
        return r


migrate = MigrateService()

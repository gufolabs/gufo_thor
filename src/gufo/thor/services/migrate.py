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
    dependencies = (postgres, mongo, liftbridge, clickhouse, consul)
    compose_depends_condition = ComposeDependsCondition.COMPLETED_SUCCESSFULLY
    compose_command = "./scripts/deploy/migrate.sh"
    compose_volumes = ["./etc/slots.cfg:/etc/slots.cfg:ro"]
    compose_environment = {"NOC_MIGRATE_SLOTS_PATH": "/etc/slots.cfg"}


migrate = MigrateService()

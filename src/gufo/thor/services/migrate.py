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
    dependencies = (postgres, mongo, liftbridge, clickhouse)
    compose_depends_condition = ComposeDependsCondition.COMPLETED_SUCCESSFULLY
    compose_command = "./noc migrate"


migrate = MigrateService()

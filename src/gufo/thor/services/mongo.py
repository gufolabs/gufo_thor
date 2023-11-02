# ---------------------------------------------------------------------
# Gufo Thor: mongo service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
mongo service.

Attributes:
    mongo: mongo service singleton.
"""

# Python modules
from pathlib import Path

# Gufo Thor modules
from .base import BaseService, ComposeDependsCondition


class MongoService(BaseService):
    """mongo service."""

    name = "mongo"
    compose_image = "mongo:4.4"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "mongo", "--eval", "db.runCommand({ ping: 1 })"],
        "interval": "3s",
        "timeout": "3s",
        "start_period": "1s",
        "retries": 10,
    }
    compose_command = "--wiredTigerCacheSizeGB 1.5 --bind_ip_all"
    compose_volumes = ["./data/mongo:/data/db"]
    compose_data_dirs = [Path("mongo")]
    service_discovery = {"mongo": 27017}


mongo = MongoService()

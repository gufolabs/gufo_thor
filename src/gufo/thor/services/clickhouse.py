# ---------------------------------------------------------------------
# Gufo Thor: clickhouse service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
clickhouse service.

Attributes:
    clickhouse: clickhouse service singleton.
"""

# Python modules
from pathlib import Path

# Gufo Thor modules
from .base import BaseService, ComposeDependsCondition


class ClickhouseService(BaseService):
    """clickhouse service."""

    name = "clickhouse"
    compose_image = "clickhouse/clickhouse-server:23"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "clickhouse-client", "--query", "SELECT 1"],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }
    compose_volumes = [
        "./data/clickhouse:/var/lib/clickhouse",
    ]
    compose_extra = {
        "cap_add": [
            "SYS_NICE",
            "NET_ADMIN",
            "IPC_LOCK",
        ],
        "ulimits": {
            "nofile": {
                "soft": 262144,
                "hard": 262144,
            }
        },
    }
    compose_data_dirs = [Path("clickhouse")]
    service_discovery = {"clickhouse": 8132}


clickhouse = ClickhouseService()

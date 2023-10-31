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
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..log import logger
from .base import BaseService, ComposeDependsCondition
from .registrator import registrator


class ClickhouseService(BaseService):
    name = "clickhouse"
    dependencies = (registrator,)
    compose_image = "clickhouse/clickhouse-server:23"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "clickhouse-client", "--query", "SELECT 1"],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }
    compose_volumes = [
        "./etc/clickhouse-server/:/etc/clickhouse-server",
        "./data/clickhouse:/var/lib/clickhouse",
    ]
    compose_environment = {
        "SERVICE_8123_NAME": "clickhouse",
        "SERVICE_9000_IGNORE": "1",
        "SERVICE_9009_IGNORE": "1",
    }
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

    def get_compose_dirs(
        self: "ClickhouseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["etc/clickhouse-server", "data/clickhouse"]

    def prepare_compose_config(
        self: "ClickhouseService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        cfg_root = Path("etc", "clickhouse-server")
        self.render_file(cfg_root / "config.xml", "config.xml")
        self.render_file(cfg_root / "users.xml", "users.xml")


clickhouse = ClickhouseService()

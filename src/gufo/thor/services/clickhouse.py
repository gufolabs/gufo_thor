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
from typing import Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
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
        "./etc/clickhouse-server/:/etc/clickhouse-server",
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
    compose_etc_dirs = [Path("clickhouse-server")]
    compose_data_dirs = [Path("clickhouse")]
    service_discovery = {"clickhouse": 8132}

    def prepare_compose_config(
        self: "ClickhouseService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        """Render configuration files."""
        cfg_root = Path("etc", "clickhouse-server")
        self.render_file(cfg_root / "config.xml", "config.xml")
        self.render_file(cfg_root / "users.xml", "users.xml")


clickhouse = ClickhouseService()

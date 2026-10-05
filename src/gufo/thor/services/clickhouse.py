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
from ..config import ServiceConfig
from ..images import get_image
from ..utils import write_file
from .base import BaseService, ComposeDependsCondition
from .db import DBService


class ClickhouseService(DBService):
    """clickhouse service."""

    name = "clickhouse"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "clickhouse-client", "--query", "SELECT 1"],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }
    compose_volumes = [
        "./etc/clickhouse/users.d:/etc/clickhouse-server/users.d",
        "./etc/clickhouse/config.d/backup.xml:"
        "/etc/clickhouse-server/config.d/backup.xml:ro",
        "clickhouse_data:/var/lib/clickhouse",
        "backup:/var/lib/clickhouse/backup",
    ]
    compose_volumes_config = {"clickhouse_data": {}}
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
    service_port = 8123
    backup_script_template = "clickhouse_backup.sh.j2"
    restore_script_template = "clickhouse_restore.sh.j2"
    backup_file_name = "clickhouse.zip"

    def get_compose_image(self, svc: ServiceConfig | None = None) -> str:
        """Get docker-compose.yml `image` section.

        Args:
            svc: Service's config from `services` part, if any.

        Returns:
            Image name.
        """
        return get_image(self.name)

    def prepare_compose_config(
        self,
        svc: ServiceConfig | None = None,
        *,
        services: list[BaseService],
    ) -> None:
        """Write configuration that allows backups to the shared volume.

        Args:
            svc: Service-specific configuration, if any.
            services: All resolved services.
        """
        write_file(
            Path("etc/clickhouse/config.d/backup.xml"),
            "<clickhouse>\n"
            "  <storage_configuration>\n"
            "    <disks>\n"
            "      <backups>\n"
            "        <type>local</type>\n"
            "        <path>/var/lib/clickhouse/backup/</path>\n"
            "      </backups>\n"
            "    </disks>\n"
            "  </storage_configuration>\n"
            "  <backups>\n"
            "    <allowed_disk>backups</allowed_disk>\n"
            "    <allowed_path>/var/lib/clickhouse/backup/</allowed_path>\n"
            "  </backups>\n"
            "</clickhouse>\n",
        )


clickhouse = ClickhouseService()

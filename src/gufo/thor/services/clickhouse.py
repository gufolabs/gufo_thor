# ---------------------------------------------------------------------
# Gufo Thor: clickhouse service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..log import logger
from .base import BaseService


class ClickhouseService(BaseService):
    name = "clickhouse"

    def get_compose_image(
        self: "ClickhouseService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        return "yandex/clickhouse-server:latest"

    def get_compose_volumes(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return [
            "./etc/clickhouse-server/:/etc/clickhouse-server",
            "./data/clickhouse:/opt/clickhouse/data",
            "./data/clickhouse/metadata:/opt/clickhouse/metadata",
            "./data/clickhouse/logs:/var/log/clickhouse-server",
        ]

    def get_compose_environment(
        self: "ClickhouseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        return {
            "SERVICE_8123_NAME": "clickhouse",
            "SERVICE_9000_IGNORE": "1",
            "SERVICE_9009_IGNORE": "1",
        }

    def get_compose_dirs(
        self: "ClickhouseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["etc/clickhouse-server", "data/clickhouse"]

    def prepare_compose_config(
        self: "ClickhouseService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        # Prepare config.xml
        path = "etc/clickhouse-server/config.xml"
        logger.info("Writing %s", path)
        with open(path, "w") as fp:
            fp.write(CONFIG_XML)


CONFIG_XML = """<?xml version="1.0"?>
<yandex>
    <logger>
        <level>trace</level>
        <log>/var/log/clickhouse-server/clickhouse-server.log</log>
        <errorlog>/var/log/clickhouse-server/clickhouse-server.err.log</errorlog>
        <size>10M</size>
        <count>1</count>
    </logger>
    <http_port>8123</http_port>
    <tcp_port>9000</tcp_port>
    <interserver_http_port>9010</interserver_http_port>
    <listen_host>0.0.0.0</listen_host>
    <max_connections>4096</max_connections>
    <keep_alive_timeout>3</keep_alive_timeout>
    <max_concurrent_queries>100</max_concurrent_queries>
    <uncompressed_cache_size>8589934592</uncompressed_cache_size>
    <mark_cache_size>5368709120</mark_cache_size>
    <path>/opt/clickhouse/data/</path>
    <tmp_path>/opt/clickhouse/tmp/</tmp_path>
    <user_files_path>/opt/clickhouse/user_files/</user_files_path>
    <users_config>users.xml</users_config>
    <default_profile>default</default_profile>
    <default_database>default</default_database>
    <macros incl="macros" optional="true" />
    <builtin_dictionaries_reload_interval>3600</builtin_dictionaries_reload_interval>
    <query_log>
        <database>system</database>
        <table>query_log</table>
        <flush_interval_milliseconds>7500</flush_interval_milliseconds>
    </query_log>
    <dictionaries_config>*_dictionary.xml</dictionaries_config>
    <compression>
    </compression>
    <resharding>
        <task_queue_path>/clickhouse/task_queue</task_queue_path>
    </resharding>
    <format_schema_path>/opt/clickhouse/format_schemas/</format_schema_path>
</yandex>
"""

clickhouse = ClickhouseService()

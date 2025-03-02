# ---------------------------------------------------------------------
# Gufo Thor: kafka service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
kafka service.

Attributes:
    kafka: kafka service singleton.
"""

# Gufo Thor modules
from .base import BaseService


class KafkaService(BaseService):
    """kafka service."""

    name = "kafka"
    compose_image = "bitnami/kafka:3.6.2"
    compose_volumes = [
        "kafka_data:/bitnami/data/",
    ]
    compose_volumes_config = {"kafka_data": {}}
    service_discovery = {"kafka": 9093}
    compose_environment = {
        "KAFKA_CFG_NODE_ID": "0",
        "KAFKA_CFG_PROCESS_ROLES": "controller,broker",
        "KAFKA_CFG_LISTENERS": "PLAINTEXT://:9092,CONTROLLER://:9093",
        "KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP": (
            "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT"
        ),
        "KAFKA_CFG_CONTROLLER_QUORUM_VOTERS": "0@kafka:9093",
        "KAFKA_CFG_CONTROLLER_LISTENER_NAMES": "CONTROLLER",
        "KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE": "false",
        # Enable fsync on sigle-node installation
        "KAFKA_CFG_LOG_FLUSH_INTERVAL_MESSAGES": "1",
        "KAFKA_CFG_LOG_FLUSH_INTERVAL_MS": "1000",
        "KAFKA_CFG_LOG_FLUSH_SCHEDULER_INTERVAL_MS": "1000",
    }


kafka = KafkaService()

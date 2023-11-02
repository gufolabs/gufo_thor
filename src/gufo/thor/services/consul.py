# ---------------------------------------------------------------------
# Gufo Thor: consul service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
consul service.

Attributes:
    consul: consul service singleton.
"""

# Python modules

# Gufo Thor modules

from .base import BaseService, ComposeDependsCondition


class ConsulService(BaseService):
    """consul service."""

    name = "consul"
    compose_image = "consul:1.15"
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": [
            "CMD",
            "curl",
            "--fail",
            "http://localhost:8500/v1/status/leader",
        ],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }
    compose_environment = {"SERVICE_IGNORE": "1"}


consul = ConsulService()

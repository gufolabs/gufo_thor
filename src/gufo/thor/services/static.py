# ---------------------------------------------------------------------
# Gufo Thor: static service
# ---------------------------------------------------------------------
# Copyright (C) 2023-24, Gufo Labs
# ---------------------------------------------------------------------
"""
static service.

Attributes:
    static: static service singleton.
"""

# NOC modules
from typing import List, Optional

# Gufo Thor modules
from gufo.thor.config import Config, ServiceConfig

from .base import ComposeDependsCondition
from .envoy import envoy
from .noc import NocService


class StaticService(NocService):
    """static service."""

    name = "static"
    dependencies = (envoy,)
    compose_command = (
        "/usr/local/bin/static-web-server "
        "--health -x --root=/opt/noc/ui "
        "--host=0.0.0.0 --port=1200"
    )
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "curl", "http://127.0.0.1:1200/health"],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }
    expose_http_prefix = "/ui/"
    rewrite_http_prefix = "/"

    def get_compose_volumes(
        self: "StaticService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """
        Get volumes section.

        Avoid /ui/pkg to be overriden.
        """
        r = super().get_compose_volumes(config, svc) or []
        if config.noc.path:
            # Preserve /ui/pkg to not be overriden with repo
            r.append("/opt/noc/ui/pkg")
        return r if r else None


static = StaticService()

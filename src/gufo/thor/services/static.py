# ---------------------------------------------------------------------
# Gufo Thor: static service
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
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

from .base import BaseService, ComposeDependsCondition, Role
from .envoy import envoy
from .noc import NOC_IMAGE_BASE


class StaticService(BaseService):
    """static service."""

    name = "static"
    dependencies = (envoy,)
    compose_command = (
        "/usr/local/bin/static-web-server "
        "--health -x --root=/www "
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
    role = Role.ASSET

    def get_compose_image(
        self, config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        """
        Get image name.

        Use tag from service's config, if any. Otherwise use tag
        from global config.
        """
        tag = config.noc.tag
        if svc and svc.tag:
            tag = svc.tag
        return f"{NOC_IMAGE_BASE}:{tag}"

    def get_compose_volumes(
        self, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """
        Get volumes section.

        Mount repo and custom when necessary.
        """
        r: List[str] = []
        # Mount UI repo inside an image
        if config.noc.ui_path:
            r.append(f"{config.noc.ui_path}:/www:cached")
        return r if r else None


static = StaticService()

# ---------------------------------------------------------------------
# Gufo Thor: static service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
static service.

Attributes:
    static: static service singleton.
"""

# Gufo Thor modules
from .base import ComposeDependsCondition
from .nginx import nginx
from .noc import NocService
from .traefik import traefik


class StaticService(NocService):
    """static service."""

    name = "static"
    dependencies = (nginx, traefik)
    compose_command = (
        "/usr/local/bin/static-web-server "
        "--health -x --root=/opt/noc/ui "
        "--host=0.0.0.0 --port=3000"
    )
    compose_depends_condition = ComposeDependsCondition.HEALTHY
    compose_healthcheck = {
        "test": ["CMD", "curl", "http://127.0.0.1:3000/health"],
        "interval": "3s",
        "timeout": "2s",
        "retries": 3,
    }
    service_discovery = {
        "static": {
            "port": 3000,
            "checks": [
                {
                    "id": "http-static-3000",
                    "interval": "1s",
                    "http": "http://static:3000/health",
                    "timeout": "1s",
                }
            ],
            "tags": [
                "traefik.enable=true",
                "traefik.http.middlewares.strip-ui.stripprefix.prefixes=/ui",
                "traefik.http.routers.static.rule=PathPrefix(`/ui`)",
                "traefik.http.routers.static.service=static",
                "traefik.http.routers.static.middlewares=strip-ui@consulcatalog",
                "traefik.http.service.static",
                "traefik.http.services.static.loadbalancer.healthcheck.path=/health",
            ],
        }
    }


static = StaticService()

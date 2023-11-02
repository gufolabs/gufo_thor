# ---------------------------------------------------------------------
# Gufo Thor: login service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
login service.

Attributes:
    login: login service singleton.
"""

# Python modules
from typing import Any, Dict, List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class LoginService(NocService):
    """
    login service.

    Also used as source of static files from nginx.
    """

    name = "login"
    dependencies = (postgres, mongo, migrate)

    def get_compose_volumes(
        self: "LoginService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """Additionaly mount static files."""
        r = super().get_compose_volumes(config, svc)
        if r is None:
            return None
        if not config.noc.path:
            # Mount static files from container
            r.append("static:/opt/noc/ui")
        return r

    def get_compose_volumes_config(
        self: "LoginService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """Additionaly add static config."""
        r = super().get_compose_volumes_config(config, svc)
        if r is None:
            r = {}
        if not config.noc.path:
            r["static"] = {}
        return r if r else None


login = LoginService()

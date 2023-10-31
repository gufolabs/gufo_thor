# ---------------------------------------------------------------------
# Gufo Thor: noc service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Python Modules
from typing import List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService


class NocService(BaseService):
    """Basic class for all NOC's services."""

    is_noc = True

    def get_compose_image(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        tag = config.noc.tag
        if svc and svc.tag:
            tag = svc.tag
        return f"dvolodin7/noc:{tag}"

    def get_compose_command(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> str | None:
        return (
            f"/usr/local/bin/python3 /opt/noc/services/{self.name}/service.py"
        )

    def get_compose_working_dir(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        return "/opt/noc"

    def get_compose_volumes(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        r: List[str] = []
        if config.noc.path:
            r.append(f"{config.noc.path}:/opt/noc")
        if config.noc.custom:
            r.append(f"{config.noc.custom}:/opt/noc_custom")
        return r if r else None

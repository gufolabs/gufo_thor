# ---------------------------------------------------------------------
# Gufo Thor: noc service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""NocService base class."""

# Python Modules
from pathlib import Path
from typing import Dict, List, Optional

# Gufo Thor modules
from ..config import Config, ServiceConfig
from .base import BaseService


class NocService(BaseService):
    """Basic class for all NOC's services."""

    is_noc = True
    name = "noc"
    compose_working_dir = "/opt/noc"
    _prepared = False

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
        if self.compose_command:
            return self.compose_command
        return (
            f"/usr/local/bin/python3 /opt/noc/services/{self.name}/service.py"
        )

    def get_compose_volumes(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        r: List[str] = ["./etc/noc/settings.yml:/opt/noc/etc/settings.yml"]
        # Mount NOC repo inside an image
        if config.noc.path:
            r.append(f"{config.noc.path}:/opt/noc")
        # Mount custom inside an image
        if config.noc.custom:
            r.append(f"{config.noc.custom}:/opt/noc_custom")
        return r if r else None

    def get_compose_environment(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        r: Dict[str, str] = {}
        if config.noc.custom:
            r["NOC_PATH_CUSTOM_PATH"] = "/opt/noc_custom"
        return r if r else None

    def get_compose_dirs(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["etc/noc"]

    def prepare_compose_config(
        self: "NocService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        if self._prepared:
            return  # Already configured from other subclass
        NocService.render_file(
            Path("etc", "noc", "settings.yml"),
            "settings.yml",
            installation_name=config.noc.installation_name,
        )


SETTINGS_YML = """installation_name: {installation_name}
"""

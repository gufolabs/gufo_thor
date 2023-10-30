# ---------------------------------------------------------------------
# Gufo Thor: consul service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Optional

# Gufo Thor modules
from gufo.thor.config import Config, ServiceConfig

from .base import BaseService


class ConsulService(BaseService):
    name = "consul"

    def get_compose_image(
        self: "ConsulService", config: Config, svc: Optional[ServiceConfig]
    ) -> str:
        return "consul:1.15"

    def get_compose_environment(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        return {"SERVICE_IGNORE": "1"}


consul = ConsulService()

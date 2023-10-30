# ---------------------------------------------------------------------
# Gufo Thor: registrator service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from typing import List, Optional

from gufo.thor.config import Config, ServiceConfig

from .base import BaseService
from .consul import consul


class RegistratorService(BaseService):
    name = "registrator"
    dependencies = (consul,)

    def get_compose_image(
        self: "RegistratorService",
        config: Config,
        svc: Optional[ServiceConfig],
    ) -> str:
        return "gliderlabs/registrator:latest"

    def get_compose_volumes(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        return ["/var/run/docker.sock:/tmp/docker.sock"]

    def get_compose_command(
        self: BaseService, config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        return "-internal consul://consul:8500"


registrator = RegistratorService()

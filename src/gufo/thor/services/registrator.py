# ---------------------------------------------------------------------
# Gufo Thor: registrator service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
registrator service.

Attributes:
    registrator: registrator service singleton.
"""

# Gufo Thor modules


from .base import BaseService
from .consul import consul


class RegistratorService(BaseService):
    """registrator service."""

    name = "registrator"
    dependencies = (consul,)
    compose_image = "gliderlabs/registrator:latest"
    compose_command = "-internal consul://consul:8500"
    compose_volumes = ["/var/run/docker.sock:/tmp/docker.sock"]


registrator = RegistratorService()

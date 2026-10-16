# ---------------------------------------------------------------------
# Gufo Thor: web service
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""
web service.

Attributes:
    web: web service singleton.
"""

# Python modules
from collections.abc import Iterable

# Gufo Thor modules
from ..config import ServiceConfig, config
from ..route import Route
from .auth import auth
from .clickhouse import clickhouse
from .envoy import envoy
from .login import login
from .migrate import migrate
from .mongo import mongo
from .noc import NocHcService
from .postgres import postgres
from .scheduler import scheduler
from .worker import worker


class WebService(NocHcService):
    """web service."""

    name = "web"
    dependencies = (
        auth,
        clickhouse,
        envoy,
        login,
        migrate,
        mongo,
        postgres,
        scheduler,
        worker,
    )
    allow_scale = True
    expose_http_prefix = "/"
    require_http_auth = True

    def iter_routes(self, svc: ServiceConfig | None = None) -> Iterable[Route]:
        """
        Iterate over web service HTTP routes.

        Args:
            svc: Service's config from `services` part, if any.

        Yields:
            The unauthenticated UI route followed by configured routes.
        """
        yield Route(name=self.name, prefix="/ui/", disable_auth=True)
        yield from super().iter_routes(svc)

    def get_compose_volumes(
        self, svc: ServiceConfig | None = None
    ) -> list[str] | None:
        """
        Get volumes section.

        Mount repo and custom when necessary.
        """
        r: list[str] = super().get_compose_volumes(svc) or []
        # Mount UI repo inside an image
        if config.noc.ui_path:
            r.append(f"{config.noc.ui_path}:/opt/noc/src/noc/ui:cached")
        return r if r else None


web = WebService()

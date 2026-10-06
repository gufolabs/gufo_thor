# ---------------------------------------------------------------------
# Gufo Thor: ComposeTarget
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""docker compose target."""

# Python modules
from operator import attrgetter
from pathlib import Path
from typing import Any, cast

# Third-party mofules
import yaml

# Gufo Thor modules
from gufo.thor import __version__

from ..artefact import ArtefactMountPoint
from ..config import config
from ..images import LEGACY_MONGO_FCV, get_version_settings
from ..labs.base import BaseLab
from ..state import state
from ..utils import ensure_directory, write_file
from .base import BaseTarget

DOT_PATH = Path(".")
LEGACY_PG_PASSWORD = "noc"  # noqa: S105 old installations uses this password


class ComposeTarget(BaseTarget):
    """
    docker compose target.

    Prepares `docker-compose.yml` and all the configuration,
    then starts with `docker compose up -d`
    """

    name = "compose"

    def prepare(self) -> None:
        """Generate docker-compose.yml, data directories, and configs."""
        super().prepare()
        print(f"gufo-thor {__version__}")
        self.migrate()
        # Prepare services and service discovery
        consul = next(svc for svc in self.services if svc.name == "consul")
        if consul:
            from ..services.consul import ConsulService

            consul = cast(ConsulService, consul)
            for svc in self.services:
                svc_cfg = config.services.get(svc.get_compose_name())
                if svc.service_port:
                    consul.register_service(svc.name, svc.service_port)
                svc.prepare_compose_config(svc_cfg, services=self.services)
        # Generate docker-compose.yml
        write_file(Path("docker-compose.yml"), self.render_config())
        # Generate .env
        env_data: list[str] = []
        if config.project is not None:
            env_data.append(f"COMPOSE_PROJECT_NAME={config.project}")
        write_file(Path(".env"), "\n".join(env_data))
        # Create assets/
        ensure_directory(Path("assets"))

    def render_config(self) -> str:
        """
        Render `docker-compose.yml`.

        Returns:
            String containing config.
        """
        s: str = yaml.safe_dump(self._get_config_dict(), sort_keys=False)
        return s

    def _get_config_dict(self) -> dict[str, Any]:
        """Get dict of docker-compose.yml."""
        r = {
            "services": self._get_services_config(),
            "networks": self._get_networks_config(),
            "volumes": self._get_volumes_config(),
            "secrets": self._get_secrets_config(),
            "configs": self._get_configs_config(),
        }
        self._apply_labs(r)
        # Remove empty sections
        for k in list(r):
            if not r[k]:
                del r[k]
        return r

    def _get_services_config(self) -> dict[str, Any]:
        """Build services section of config."""
        # Resolve services
        return {
            svc.get_compose_name(): svc.get_compose_config(
                config.services.get(svc.get_compose_name())
            )
            for svc in self.services
        }

    def _get_networks_config(self) -> dict[str, Any]:
        """Build networks section of config."""
        r: dict[str, dict[str, Any]] = {
            "noc": {
                "driver": "bridge",
            }
        }
        for pool_name, pool in config.pools.items():
            r[f"pool-{pool_name}"] = {
                "driver": "bridge",
                "internal": True,
                "driver_opts": {
                    "com.docker.network.bridge.inhibit_ipv4": "true"
                },
                "ipam": {
                    "config": [
                        {
                            "subnet": str(pool.subnet),
                        }
                    ]
                },
            }
        return r

    def _get_volumes_config(self) -> dict[str, Any]:
        """Build volumes section of config."""
        r: dict[str, dict[str, Any]] = {}
        for svc in self.services:
            vc = svc.get_compose_volumes_config(config.services.get(svc.name))
            if not vc:
                continue
            for n, c in vc.items():
                if n in r:
                    r[n].update(c)
                else:
                    r[n] = c
        return r

    def _get_secrets_config(self) -> dict[str, Any]:
        """Build secrets section of config."""
        r: dict[str, dict[str, Any]] = {}
        for svc in self.services:
            secrets = svc.get_compose_secrets(config.services.get(svc.name))
            if not secrets:
                continue
            for s in secrets:
                s.ensure_secret()
                r[s.name] = {"file": str(DOT_PATH / s.path)}
        return r

    def _get_configs_config(self) -> dict[str, Any]:
        """Build configs section of config."""
        mounts: set[ArtefactMountPoint] = set()
        for svc in self.services:
            configs = svc.get_compose_configs(config.services.get(svc.name))
            if not configs:
                continue
            for cfg in configs:
                mounts.update(cfg.iter_mounts())
        r: dict[str, Any] = {}
        for mount in sorted(mounts, key=attrgetter("name")):
            r[mount.name] = {"file": str(mount.local_path)}
        return r

    def _apply_labs(self, cfg: dict[str, Any]) -> None:
        """Apply labs section."""
        if not config.labs:
            return
        if "services" not in cfg:
            cfg["services"] = {}
        networks = {}
        for lab_name, lab_config in config.labs.items():
            for node_name, node_config in lab_config.nodes.items():
                svc_name = f"lab-{lab_name}-{node_name}"
                lab = BaseLab.get(node_config.type)
                cfg["services"][svc_name] = lab.get_compose_config(
                    config, lab_config, node_config
                )
            for n, link in enumerate(lab_config.links):
                link_cfg: dict[str, Any] = {"driver": "bridge"}
                if link.prefix:
                    link_cfg.update(
                        {
                            "internal": True,
                            "driver_opts": {
                                "com.docker.network.bridge.inhibit_ipv4": (
                                    "true"
                                )
                            },
                            "ipam": {"config": [{"subnet": str(link.prefix)}]},
                        }
                    )

                networks[f"lab-{lab_config.name}-l{n}"] = link_cfg
        if networks:
            if "networks" not in cfg:
                cfg["networks"] = {}
            cfg["networks"].update(networks)

    def migrate(self) -> None:
        """Migrate configs."""
        from ..services.noc import noc_settings

        first_install = not noc_settings.local_path.exists()
        self.process_mongo_fcv(first_install)
        if not first_install:
            self.migrate_postgres_password()

    def migrate_postgres_password(self) -> None:
        """Migrate default postgres password."""
        from ..secret import postgres_password

        if not postgres_password.path.exists():
            postgres_password.set_secret(LEGACY_PG_PASSWORD)

    def process_mongo_fcv(self, first_install: bool) -> None:
        """Initializes the stored MongoDB FCV for new and legacy installations.

        For existing installations, raises an error if the stored FCV does not
        match the FCV expected by the configured NOC version.

        Args:
            first_install: Whether this is the first installation of Thor.

        Raises:
            RuntimeError: If the stored MongoDB FCV does not match the FCV
                expected by the configured NOC version.
        """
        vs = get_version_settings()
        if state.mongo_fcv is None:
            state.mongo_fcv = (
                vs.target_mongo_fcv if first_install else LEGACY_MONGO_FCV
            )
            state.save()
            return
        if state.mongo_fcv != vs.target_mongo_fcv:
            msg = (
                "Mongo FCV mismatch. "
                f"Expected {vs.target_mongo_fcv}, got {state.mongo_fcv}. "
                "Run gufo-thor migrate-mongo to fix."
            )
            raise RuntimeError(msg)

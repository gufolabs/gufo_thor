# ---------------------------------------------------------------------
# Gufo Thor: ComposeTarget
# ---------------------------------------------------------------------
# Copyright (C) 2023-24, Gufo Labs
# ---------------------------------------------------------------------
"""docker compose target."""

# Python modules
import json
from pathlib import Path
from typing import Any, Dict, List, Union

# Third-party mofules
import yaml

# Gufo Thor modules
from gufo.thor import __version__

from ..labs.base import BaseLab
from ..services.base import BaseService
from ..utils import ensure_directory, write_file
from .base import BaseTarget

DOT_PATH = Path(".")


class ComposeTarget(BaseTarget):
    """
    docker compose target.

    Prepares `docker-compose.yml` and all the configuration,
    then starts with `docker compose up -d`
    """

    name = "compose"

    def prepare(self: "ComposeTarget") -> None:
        """Generate docker-compose.yml, data directories, and configs."""
        print(f"gufo-thor {__version__}")
        # Generate docker-compose.yml
        write_file(Path("docker-compose.yml"), self.render_config())
        # Generate .env
        env_data: List[str] = []
        if self.config.project is not None:
            env_data.append(f"COMPOSE_PROJECT_NAME={self.config.project}")
        write_file(Path(".env"), "\n".join(env_data))
        # Create etc/
        etc = Path("etc")
        ensure_directory(etc)
        # Create assets/
        ensure_directory(Path("assets"))
        # Generate directories and configs
        services = list(BaseService.resolve(self.config.services))
        for svc in services:
            svc_cfg = self.config.services.get(svc.get_compose_name())
            # Create config
            svc.prepare_compose_config(self.config, svc_cfg, services)
            # Service discovery
            sd = svc.get_service_discovery(self.config, svc_cfg)
            if sd:
                self._configure_service_discovery(svc.name, sd)

    def render_config(self: "ComposeTarget") -> str:
        """
        Render `docker-compose.yml`.

        Returns:
            String containing config.
        """
        s: str = yaml.safe_dump(self._get_config_dict(), sort_keys=False)
        return s

    def _get_config_dict(self: "ComposeTarget") -> Dict[str, Any]:
        """Get dict of docker-compose.yml."""
        r = {
            "services": self._get_services_config(),
            "networks": self._get_networks_config(),
            "volumes": self._get_volumes_config(),
            "secrets": self._get_secrets_config(),
        }
        self._apply_labs(r)
        # Remove empty sections
        for k in list(r):
            if not r[k]:
                del r[k]
        return r

    def _get_services_config(self: "ComposeTarget") -> Dict[str, Any]:
        """Build services section of config."""
        # Resolve services
        return {
            svc.get_compose_name(): svc.get_compose_config(
                self.config, self.config.services.get(svc.get_compose_name())
            )
            for svc in BaseService.resolve(self.config.services)
        }

    def _get_networks_config(self: "ComposeTarget") -> Dict[str, Any]:
        """Build networks section of config."""
        r: Dict[str, Dict[str, Any]] = {
            "noc": {
                "driver": "bridge",
            }
        }
        for pool_name, pool in self.config.pools.items():
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

    def _get_volumes_config(self: "ComposeTarget") -> Dict[str, Any]:
        """Build volumes section of config."""
        r: Dict[str, Dict[str, Any]] = {}
        for svc in BaseService.resolve(self.config.services):
            vc = svc.get_compose_volumes_config(
                self.config, self.config.services.get(svc.name)
            )
            if not vc:
                continue
            for n, c in vc.items():
                if n in r:
                    r[n].update(c)
                else:
                    r[n] = c
        return r

    def _get_secrets_config(self) -> Dict[str, Any]:
        """Build secrets section of config."""
        r: Dict[str, Dict[str, Any]] = {}
        for svc in BaseService.resolve(self.config.services):
            secrets = svc.get_compose_secrets(
                self.config, self.config.services.get(svc.name)
            )
            if not secrets:
                continue
            for s in secrets:
                s.ensure_secret()
                r[s.name] = {"file": str(DOT_PATH / s.path)}
        return r

    def _apply_labs(self, cfg: Dict[str, Any]) -> None:
        """Apply labs section."""
        if not self.config.labs:
            return
        if "services" not in cfg:
            cfg["services"] = {}
        networks = {}
        for lab_name, lab_config in self.config.labs.items():
            for node_name, node_config in lab_config.nodes.items():
                svc_name = f"lab-{lab_name}-{node_name}"
                lab = BaseLab.get(node_config.type)
                cfg["services"][svc_name] = lab.get_compose_config(
                    self.config, lab_config, node_config
                )
            for n, link in enumerate(lab_config.links):
                link_cfg: Dict[str, Any] = {"driver": "bridge"}
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

    def _configure_service_discovery(
        self: "ComposeTarget",
        name: str,
        sd: Dict[str, Union[int, Dict[str, Any]]],
    ) -> None:
        """Prepare service discovery config."""
        sd_root = Path("etc", "consul")
        ensure_directory(sd_root)
        for svc_name, sd_cfg in sd.items():
            cfg: Dict[str, Any] = {
                "name": svc_name,
                "address": name,
            }
            if isinstance(sd_cfg, int):
                # Port
                port = sd_cfg
                cfg.update(
                    {
                        "port": port,
                        "checks": [
                            {
                                "id": f"tcp-{svc_name}-{port}",
                                "interval": "1s",
                                "tcp": f"{name}:{port}",
                                "timeout": "1s",
                            }
                        ],
                    }
                )
            else:
                cfg.update(sd_cfg)
                if "port" not in cfg:
                    msg = "port is not set"
                    raise ValueError(msg)
            path = sd_root / f"{svc_name}-{cfg['port']}.json"
            write_file(path, json.dumps({"service": cfg}))

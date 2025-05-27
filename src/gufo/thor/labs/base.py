# ---------------------------------------------------------------------
# Gufo Thor: BaseLab
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""
BaseLab definition.

Attributes:
    loader: The lab loader.
"""

# Python modules
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Type, Union

# Third-party modules
import jinja2

from gufo.loader import Loader

# Gufo Thor modules
from ..config import Config, LabConfig, LabNodeConfig
from ..utils import write_file


class BaseLab(object):
    """Router for lab."""

    name: str
    image: str

    def get_compose_config(
        self, config: Config, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> Dict[str, Any]:
        """Generate service config for docker compose."""
        r: Dict[str, Any] = {
            "image": self.get_compose_image(config, lab_config, node_config),
            "restart": "no",
            "privileged": True,
        }
        volumes = self.get_compose_volumes(config, lab_config, node_config)
        if volumes:
            r["volumes"] = volumes
        networks = self.get_compose_networks(config, lab_config, node_config)
        if networks:
            r["networks"] = networks
        return r

    def get_compose_image(
        self, config: Config, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> str:
        """Generate compose image name."""
        if node_config.version:
            return f"{self.image}:{node_config.version}"
        return self.image

    def get_compose_networks(
        self, config: Config, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> List[str]:
        """Get volumes settings."""
        return [
            f"{lab_config.name}-l{n}"
            for n, link in enumerate(lab_config.links)
            if node_config.name in {link.node_a, link.node_z}
        ]

    def get_compose_volumes(
        self, config: Config, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> List[str]:
        """Get service network settings."""
        return []

    @staticmethod
    def get(name: str) -> "BaseLab":
        """Get Lab instance."""
        return loader[name]()

    def get_config_dir(
        self, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> Path:
        """Get root of the configuration directory."""
        return Path("etc", "labs", lab_config.name, "conf", node_config.name)

    @classmethod
    def render_file(
        cls: Type["BaseLab"],
        path: Path,
        tpl: str,
        **kwargs: Union[str, int, List[Any]],
    ) -> None:
        """
        Apply a context to the template and write to file.

        Args:
            path: File path
            tpl: Template name (relative to `gufo.thor.templates`)
            kwargs: Template context
        """
        # Load template
        # Warning: joinpath() accepts only one
        # parameter on Py3.9 and Py3.10
        data = (
            resources.files("gufo.thor")
            .joinpath("templates")
            .joinpath("labs")
            .joinpath(cls.name)
            .joinpath(tpl)
            .read_text()
        )
        template = jinja2.Template(data)
        data = template.render(**kwargs)
        # Write file
        write_file(path, data)


loader = Loader[Type[BaseLab]](base="gufo.thor.labs", exclude=("base", "noc"))

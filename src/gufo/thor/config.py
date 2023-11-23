# ---------------------------------------------------------------------
# Gufo Thor: Command-line utility
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""Config data structures."""

# Python Modules
from dataclasses import dataclass
from importlib import resources
from typing import Any, Dict, Optional

# Third-party modules
import yaml


@dataclass
class NocConfig(object):
    """
    The `noc` section of the config.

    Attributes:
        tag: NOC image tag
        path: An optional path to the NOC source code. If not empty,
            image's `/opt/noc`vwill be replaced with path
        custom: Optional path to the custom, will be mounted
            in the `/opt/noc_custom` directory.
        installation_name: The installation name which will be shown
            in the interface.
    """

    tag: str = "master"
    path: Optional[str] = None
    custom: Optional[str] = None
    installation_name: str = "Unconfigured Installation"

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "NocConfig":
        """
        Generate NocConfig instance from a dictionary.

        Args:
            data: Incoming data.

        Returns:
            A configured NocConfig instance.
        """
        return NocConfig(**data)


@dataclass
class ExposeConfig(object):
    """
    The `expose` section of the config.

    Attributes:
        domain_name: A domain name through which the NOC's user interface
            will be accessed in browser.
        port: An HTTPS port of the NOC's user interface.
    """

    domain_name: str = "go.getnoc.com"
    port: int = 32777

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExposeConfig":
        """
        Generate ExposeConfig instance from a dictionary.

        Args:
        data: Incoming data.

        Returns:
        A configured ExposeConfig instance.
        """
        return ExposeConfig(**data)


@dataclass
class ServiceConfig(object):
    """
    The `services` section of the config.

    Attributes:
        tag: Override `noc.tag` setting for a service if not empty.
        enabled: True, if the service is enabled.
    """

    tag: Optional[str] = None
    enabled: bool = True

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ServiceConfig":
        """
        Generate ServiceConfig instance from a dictionary.

        Args:
            data: Incoming data.

        Returns:
            A configured ServiceConfig instance.
        """
        return ServiceConfig(**data)

    @staticmethod
    def default() -> "ServiceConfig":
        """Get default ServiceConfig."""
        return ServiceConfig(tag=None, enabled=True)


@dataclass
class Config(object):
    """
    The Gufo Thor config.

    Attributes:
        noc: The `noc` section of the config.
        expose: The `expose` section of the config.
        services: The `services` section of the config.
    """

    noc: NocConfig
    expose: ExposeConfig
    services: Dict[str, ServiceConfig]

    @staticmethod
    def from_yaml(data: str) -> "Config":
        """
        Parse YAML file and return an instance of the Config.

        Args:
            data: String containing YAML config.


        Returns:
            An Config instance.
        """
        cfg = yaml.safe_load(data)
        if not isinstance(cfg, dict):
            msg = "Config must be dict"
            raise ValueError(msg)
        noc_cfg = NocConfig.from_dict(cfg["noc"])
        expose_cfg = ExposeConfig.from_dict(cfg["expose"])
        services: Dict[str, ServiceConfig] = {}
        data_svc: Any = cfg.get("services", [])
        if isinstance(data_svc, list):
            services = {x: ServiceConfig.default() for x in data_svc}
        elif isinstance(data_svc, dict):
            services = {x: ServiceConfig.from_dict(y) for x, y in data_svc}
        else:
            msg = f"services must be list or dict, not {type(data_svc)}"
            raise ValueError(msg)
        return Config(noc=noc_cfg, expose=expose_cfg, services=services)

    @staticmethod
    def default() -> "Config":
        """
        Generate default config.

        Returns:
            An Config instance
        """
        noc_cfg = NocConfig()
        expose_cfg = ExposeConfig()
        return Config(noc=noc_cfg, expose=expose_cfg, services={})


def get_sample(name: str) -> str:
    """
    Get preconfigured config sample by name.

    All samples are preserved in `samples` directory.

    Args:
        name: Sample name, without `.yml` extension.

    Returns:
        A string containinng sample code.
    """
    # Warning: joinpath() accepts only one
    # parameter on Py3.9 and Py3.10
    return (
        resources.files("gufo.thor")
        .joinpath("samples")
        .joinpath(f"{name}.yml")
        .read_text()
    )

# ---------------------------------------------------------------------
# Gufo Thor: Command-line utility
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Config data structures."""

# Python Modules
from dataclasses import dataclass
from importlib import resources
from typing import Any, Dict, Literal, Optional, Union

# Third-party modules
import yaml

# Gufo Thor modules
from .log import logger

LOCALHOST = "127.0.0.1"
ALL = "0.0.0.0"

DEFAULT_WEB_PORT = 32777


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
        theme: Web interface theme. One of: `noc`, `gray`.
        migrate: Run migrations on start
        config: User-defined config.
    """

    tag: str = "master"
    path: Optional[str] = None
    custom: Optional[str] = None
    installation_name: str = "Unconfigured Installation"
    theme: Literal["noc", "gray"] = "noc"
    migrate: bool = True
    config: Optional[Dict[str, Any]] = None

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
class Listen(object):
    """
    Listener configuration.

    Used to proxy host's ports into the container.

    Accepts formats:
    ```
    * <port>
    * "<port>"
    * "<address>:<port>"
    * {"port": <port>}
    * {"address": "<address>", "port": <port>}
    ```

    Attributes:
        address: Listen address.
        port: Listen port.
    """

    address: str
    port: int

    @staticmethod
    def from_dict(data: Union[dict[str, Any], int, str]) -> "Listen":
        """
        Generate listener from data.

        Args:
            data: Incoming data.

        Returns:
            A configured Listener instance.
        """
        if isinstance(data, int):
            return Listen(address=LOCALHOST, port=data)
        if isinstance(data, str):
            if ":" in data:
                addr, port = data.rsplit(":", 1)
                return Listen(address=addr, port=int(port))
            return Listen(address=LOCALHOST, port=int(data))
        return Listen(
            address=data.get("address", LOCALHOST), port=data["port"]
        )

    def docker_compose_port(self: "Listen", container_port: int) -> str:
        """
        Generate configuration for port forwarding.

        Args:
            container_port: Port in the container.

        Returns:
            Port configuration for docker compose.
        """
        return f"{self.address}:{self.port}:{container_port}"


@dataclass
class ExposeConfig(object):
    """
    The `expose` section of the config.

    Attributes:
        domain_name: A domain name through which the NOC's user interface
            will be accessed in browser.
        web: Web listener configuration.
        port: An HTTPS port of the NOC's user interface (deprecated).
        open_browser: Open browser on startup.
    """

    domain_name: str = "go.getnoc.com"
    web: Optional[Listen] = None
    open_browser: bool = True

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExposeConfig":
        """
        Generate ExposeConfig instance from a dictionary.

        Args:
            data: Incoming data.

        Returns:
            A configured ExposeConfig instance.
        """
        data = data.copy()
        # Decode web
        if "web" in data:
            data["web"] = Listen.from_dict(data["web"])
        elif "port" in data:
            data["web"] = Listen.from_dict(data["port"])
        else:
            data["web"] = Listen(address=LOCALHOST, port=DEFAULT_WEB_PORT)
        # Deprecated port option
        if data.get("port"):
            port = data.pop("port")
            logger.warning("Using obsolete `expose.port` configuration.")
            logger.warning("In thor.yml replace:")
            logger.warning(">>>>>\nexpose:\n  port: %s\n<<<<<", port)
            logger.warning("with:")
            logger.warning(">>>>>\nexpose:\n  web:\n    port: %s\n<<<<<", port)
        return ExposeConfig(**data)


@dataclass
class ServiceConfig(object):
    """
    The `services` section of the config.

    Attributes:
        tag: Override `noc.tag` setting for a service if not empty.
        scale: Number of concurrently running servers. 0 - disable.
    """

    tag: Optional[str] = None
    scale: int = 1

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
        return ServiceConfig(tag=None, scale=1)


@dataclass
class CliConfig(object):
    """
    Config populated during runtime.

    Should not be set by user. Populated
    from CLI options.
    """


@dataclass
class Config(object):
    """
    The Gufo Thor config.

    Attributes:
        project: Optional project name used to prefix
            the services and volumes. If not set - directory
            name is used. Should be unique within Thor projects
            on same host.
        noc: The `noc` section of the config.
        expose: The `expose` section of the config.
        services: The `services` section of the config.
    """

    project: Optional[str]
    noc: NocConfig
    expose: ExposeConfig
    services: Dict[str, ServiceConfig]
    cli: CliConfig

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
            services = {
                x: ServiceConfig.from_dict(y) for x, y in data_svc.items()
            }
        else:
            msg = f"services must be list or dict, not {type(data_svc)}"
            raise ValueError(msg)
        return Config(
            project=cfg.get("project"),
            noc=noc_cfg,
            expose=expose_cfg,
            services=services,
            cli=CliConfig(),
        )

    @staticmethod
    def default() -> "Config":
        """
        Generate default config.

        Returns:
            An Config instance
        """
        noc_cfg = NocConfig()
        expose_cfg = ExposeConfig()
        return Config(
            project=None,
            noc=noc_cfg,
            expose=expose_cfg,
            services={},
            cli=CliConfig(),
        )


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

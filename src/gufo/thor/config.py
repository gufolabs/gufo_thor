# ---------------------------------------------------------------------
# Gufo Thor: Config
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Config data structures."""

# Python Modules
from collections import defaultdict
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import (
    Any,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    cast,
)

# Third-party modules
import yaml

from .ip import IPv4Address, IPv4Prefix
from .log import logger

# Gufo Thor modules
from .secret import Secret
from .validator import as_int, as_ipv4, as_ipv4_prefix, as_str, errors

DEFAULT_DOMAIN = "go.getnoc.com"
LOCALHOST = "127.0.0.1"
WILDCARD = "0.0.0.0"  # noqa:S104
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
        # Check secrets
        cfg = data.get("config")
        if cfg:
            with errors.context("config"):
                for s in Secret.iter_secrets():
                    s.check_config(cfg)
        return NocConfig(**data)

    @staticmethod
    def default() -> "NocConfig":
        """
        Get default NocConfig.

        Returns:
            NocConfig instance.
        """
        return NocConfig()


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
        mtls_ca_cert: When set, enables mTLS and defines CA certificate path,
            relative to `assets`
    """

    domain_name: str = DEFAULT_DOMAIN
    web: Optional[Listen] = None
    mongo: Optional[Listen] = None
    postgres: Optional[Listen] = None
    open_browser: bool = True
    mtls_ca_cert: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExposeConfig":
        """
        Generate ExposeConfig instance from a dictionary.

        Args:
            data: Incoming data.

        Returns:
            A configured ExposeConfig instance.
        """
        # @todo: Rewrite using with errors.context
        data = data.copy()
        # Decode web
        if "web" in data:
            web_cfg = data["web"]
            # Alter defaults for non-default domains
            if (
                "address" not in web_cfg
                and data.get("domain_name", "") != DEFAULT_DOMAIN
            ):
                # Bind to all addresses for non-default domain
                web_cfg["address"] = WILDCARD
            data["web"] = Listen.from_dict(web_cfg)
        elif "port" in data:
            data["web"] = Listen.from_dict(data["port"])
        else:
            data["web"] = Listen(address=LOCALHOST, port=DEFAULT_WEB_PORT)
        # Decode mongo
        if "mongo" in data:
            data["mongo"] = Listen.from_dict(data["mongo"])
        if "postgres" in data:
            data["postgres"] = Listen.from_dict(data["postgres"])
        # mTLS
        if "mtls_ca_cert" in data:
            # Check
            with errors.context("mtls_ca_cert"):
                path = Path("assets") / Path(data["mtls_ca_cert"])
                if not path.exists():
                    errors.error(
                        f"File {path} is not found. "
                        "Place proper CA certificate to enable mTLS"
                    )
        # Deprecated port option
        if data.get("port"):
            port = data.pop("port")
            logger.warning("Using obsolete `expose.port` configuration.")
            logger.warning("In thor.yml replace:")
            logger.warning(">>>>>\nexpose:\n  port: %s\n<<<<<", port)
            logger.warning("with:")
            logger.warning(">>>>>\nexpose:\n  web:\n    port: %s\n<<<<<", port)
        return ExposeConfig(**data)

    @staticmethod
    def default() -> "ExposeConfig":
        """
        Get default ExposeConfig.

        Returns:
            ExposeConfig instance.
        """
        return ExposeConfig()


@dataclass
class PoolAddressConfig(object):
    """
    Pool addresses configuration.

    Attributes:
        gw: Gateway address for `pool-gw`.
        syslog: Syslog collector address.
        trap: SNMP trap address.
    """

    gw: Optional[IPv4Address] = None
    syslog: Optional[IPv4Address] = None
    trap: Optional[IPv4Address] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PoolAddressConfig":
        """Get addresses config from dict."""
        with errors.context("address"):
            r = PoolAddressConfig(
                gw=as_ipv4(data, "gw", required=False),
                syslog=as_ipv4(data, "syslog", required=False),
                trap=as_ipv4(data, "trap", required=False),
            )
            # Check for overlaps
            used: DefaultDict[str, List[str]] = defaultdict(list)
            if r.gw:
                used[str(r.gw)].append("gw")
            if r.syslog:
                used[str(r.syslog)].append("syslog")
            if r.trap:
                used[str(r.trap)].append("trap")
            for addr, names in used.items():
                if len(names) > 1:
                    for n in names:
                        with errors.context(n):
                            nl = ", ".join(x for x in names if n != x)
                            errors.error(
                                f"address {addr} is already used in {nl}"
                            )
            return r

    def iter_used(self) -> Iterable[IPv4Address]:
        """Iterate all used addresses."""
        if self.gw:
            yield self.gw
        if self.syslog:
            yield self.syslog
        if self.trap:
            yield self.trap


@dataclass
class PoolConfig(object):
    """
    The `pools` section of config.

    Attributes:
        name: Pool name.
        subnet: Allocated subnet.
    """

    name: str
    subnet: IPv4Prefix
    address: PoolAddressConfig

    @staticmethod
    def from_dict(name: str, data: Dict[str, Any]) -> "PoolConfig":
        """
        Generate PoolConfig instance from a dictionary.

        Args:
            name: Pool name.
            data: Incoming data.

        Returns:
            A configured PoolConfig instance.
        """
        return PoolConfig(
            name=name,
            subnet=as_ipv4_prefix(data, "subnet", required=True),
            address=PoolAddressConfig.from_dict(data.get("address") or {}),
        )


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
class LabNodeUserCredentials(object):
    """
    User credentials.

    Attributes:
        user: Local user name.
        password: Plain-text password.
    """

    user: str
    password: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LabNodeUserCredentials":
        """Get user credentials from dict."""
        return LabNodeUserCredentials(
            user=as_str(data, "user", required=True),
            password=as_str(data, "password", required=True),
        )


@dataclass
class LabNodeSnmpV2cCredentials(TypedDict):
    """SNMP v2c Credentials."""

    version: Literal["v2c"]
    community: str


LabNodeSnmpCredentials = LabNodeSnmpV2cCredentials


@dataclass
class LabNodeConfig(object):
    """The `labs.nodes` section of config."""

    name: str
    type: str
    version: Optional[str] = None
    router_id: Optional[IPv4Address] = None
    pool_gw: bool = False
    users: Optional[List[LabNodeUserCredentials]] = None
    snmp: Optional[List[LabNodeSnmpCredentials]] = None

    @staticmethod
    def from_dict(
        name: str, data: Dict[str, Optional[str]]
    ) -> "LabNodeConfig":
        """
        Generate LabNodeConfig from dict.

        Args:
            name: Node name.
            data: Incoming data.

        Returns:
            LabNodeConfig instance.
        """
        users_cfg = data.get("users")
        users: List[LabNodeUserCredentials] = []
        if users_cfg:
            with errors.context("users"):
                if isinstance(users_cfg, list):
                    for n, u in enumerate(users_cfg):
                        with errors.context(str(n)):
                            users.append(LabNodeUserCredentials.from_dict(u))
                else:
                    errors.error("must be list")
        # Snmp
        snmp: List[LabNodeSnmpCredentials] = []
        snmp_cfg = data.get("snmp")
        if snmp_cfg:
            with errors.context("snmp"):
                if isinstance(snmp_cfg, list):
                    for n, s in enumerate(snmp_cfg):
                        with errors.context(str(n)):
                            version = s.get("version")
                            if not version:
                                errors.error("must contain version")
                            elif version == "v2c":
                                snmp.append(
                                    LabNodeSnmpV2cCredentials(
                                        version="v2c",
                                        community=as_str(
                                            s, "community", required=True
                                        ),
                                    )
                                )
                            else:
                                errors.error("version must be v2c")
                else:
                    errors.error("must be list")
        return LabNodeConfig(
            name=name,
            type=as_str(data, "type", required=True),
            version=as_str(data, "version", required=False),
            router_id=as_ipv4(data, "router-id", required=False),
            pool_gw=bool(data.get("pool-gw")),
            users=users or None,
            snmp=snmp or None,
        )


@dataclass
class IsisLinkProtocolConfig(object):
    """ISIS protocol configuration for link."""

    metric: Optional[int] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "IsisLinkProtocolConfig":
        """
        Generate IsisLinkProtocolConfig from dict.

        Args:
            data: Incoming data.

        Returns:
            IsisLinkProtocolConfig instance.
        """
        return IsisLinkProtocolConfig(
            metric=as_int(data, "metric", required=False)
        )


class LinkProtocolConfig(TypedDict, total=False):
    """Protocol settings."""

    isis: IsisLinkProtocolConfig


@dataclass
class LabLinkConfig(object):
    """Link item."""

    prefix: IPv4Prefix
    node_a: str
    node_z: str
    protocols: LinkProtocolConfig

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LabLinkConfig":
        """Create link item from config."""
        # Build protocols
        protocols: LinkProtocolConfig = {}
        with errors.context("protocols"):
            for proto_name, proto_conf in data.get("protocols", {}).items():
                if proto_name == "isis":
                    protocols["isis"] = IsisLinkProtocolConfig.from_dict(
                        proto_conf
                    )
                else:
                    errors.error("Unknown protocol")
        return LabLinkConfig(
            prefix=IPv4Prefix(as_str(data, "prefix", required=True)),
            node_a=as_str(data, "node-a", required=True),
            node_z=as_str(data, "node-z", required=True),
            protocols=protocols,
        )


@dataclass
class LabConfig(object):
    """
    The `labs` section of the config.

    Attributes:
        name: lab name.
        nodes: Nodes configuration.
        pool: Lab pool.

    """

    name: str
    nodes: Dict[str, LabNodeConfig]
    links: List[LabLinkConfig]
    pool: Optional[str] = None

    @staticmethod
    def from_dict(name: str, data: Dict[str, Any]) -> "LabConfig":
        """
        Generate LabConfig instance from a dictionary.

        Args:
            name: Lab name.
            data: Incoming data.

        Returns:
            A configured LabConfig instance.
        """
        pool = as_str(data, "pool", required=False)
        with errors.context(name):
            # Process nodes
            nodes: Dict[str, LabNodeConfig] = {}
            with errors.context("nodes"):
                for x, y in data.get("nodes", {}).items():
                    node_name = str(x)
                    with errors.context(node_name):
                        nodes[node_name] = LabNodeConfig.from_dict(
                            node_name, y
                        )
                # Validate nodes
                if pool:
                    n_gw = sum(1 for n in nodes.values() if n.pool_gw)
                    if not n_gw:
                        with errors.context(".."):
                            errors.error(
                                "`pool-gw` must be set on one of the nodes"
                            )
                    elif n_gw > 1:
                        p_gw = [n for n in nodes.values() if n.pool_gw]
                        p_gw_list = ", ".join(n.name for n in p_gw)
                        for n in p_gw:
                            with errors.context(["nodes", n.name, "pool-gw"]):
                                errors.error(
                                    f"multiple pool-gw set ({p_gw_list})"
                                )
            # Process links
            links: List[LabLinkConfig] = []
            with errors.context("links"):
                for n_link, x in enumerate(data.get("links", [])):
                    with errors.context(str(n_link)):
                        links.append(LabLinkConfig.from_dict(x))
            return LabConfig(
                name=name,
                nodes=nodes,
                links=links,
                pool=pool,
            )

    def check(self) -> None:
        """Check config."""
        # Check router-id for uniqueness
        # collect
        seen: DefaultDict[str, List[str]] = defaultdict(list)
        for node_name, node in self.nodes.items():
            if node.router_id:
                seen[str(node.router_id)].append(node_name)
        # Validate
        for router_id, node_names in seen.items():
            if len(node_names) > 1:
                nl = ", ".join(node_names)
                for node_name in node_names:
                    with errors.context(["nodes", node_name, "router-id"]):
                        errors.error(
                            f"router-id `{router_id}` is not unique. "
                            f"Occured in {nl}"
                        )


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
        labs: The `labs` section of the config.
    """

    project: Optional[str]
    noc: NocConfig
    expose: ExposeConfig
    pools: Dict[str, PoolConfig]
    services: Dict[str, ServiceConfig]
    cli: CliConfig
    labs: Dict[str, LabConfig]

    @staticmethod
    def from_file(path: Union[Path, str]) -> "Config":
        """
        Read file and return instance of the Config.

        Dies if config contains errors.

        Args:
            path: File path.

        Returns:
            Config instance.
        """
        try:
            with open(path) as fp:
                return Config.from_yaml(fp.read())
        except OSError as e:
            errors.die(f"Cannot read file {path}: {e}")

    @staticmethod
    def _parse_yaml(data: str) -> Dict[str, Any]:
        cfg = yaml.safe_load(data)
        if not isinstance(cfg, dict):
            errors.die("Config must be dict")
        return cast(Dict[str, Any], cfg)

    @staticmethod
    def _parse_noc(data: Dict[str, Any]) -> NocConfig:
        with errors.context("noc"):
            cfg = data.get("noc")
            if cfg is None:
                return NocConfig.default()
            return NocConfig.from_dict(cfg)

    @staticmethod
    def _parse_expose(data: Dict[str, Any]) -> ExposeConfig:
        with errors.context("expose"):
            cfg = data.get("expose")
            if cfg is None:
                return ExposeConfig.default()
            return ExposeConfig.from_dict(cfg)

    @staticmethod
    def _parse_pools(data: Dict[str, Any]) -> Dict[str, PoolConfig]:
        with errors.context("pools"):
            cfg = data.get("pools")
            if not cfg:
                return {}
            if not isinstance(cfg, dict):
                errors.error("must be dict")
                return {}
            r = {}
            for pool_name, pool_cfg in cfg.items():
                pn = str(pool_name)
                with errors.context(pn):
                    r[pool_name] = PoolConfig.from_dict(pn, pool_cfg)
            return r

    @staticmethod
    def _parse_services(data: Dict[str, Any]) -> Dict[str, ServiceConfig]:
        with errors.context("services"):
            cfg = data.get("services")
            if not cfg:
                errors.error("must be set")
                return {}
            services: Dict[str, ServiceConfig]
            if isinstance(cfg, list):
                services = {x: ServiceConfig.default() for x in cfg}
            elif isinstance(cfg, dict):
                services = {
                    x: ServiceConfig.from_dict(y) for x, y in cfg.items()
                }
            else:
                errors.error(f"services must be list or dict, not {type(cfg)}")
                services = {}
            return services

    @staticmethod
    def _parse_labs(data: Dict[str, Any]) -> Dict[str, LabConfig]:
        with errors.context("labs"):
            cfg = data.get("labs")
            if not cfg:
                return {}
            if not isinstance(cfg, dict):
                errors.error("must be dict")
                return {}
            labs: Dict[str, LabConfig] = {}
            for x, y in cfg.items():
                lab_name = str(x)
                lab = LabConfig.from_dict(lab_name, y)
                with errors.context(lab_name):
                    lab.check()
                labs[lab_name] = lab
            return labs

    @staticmethod
    def from_yaml(data: str) -> "Config":
        """
        Parse YAML file and return an instance of the Config.

        Dies if config contains errors.

        Args:
            data: String containing YAML config.

        Returns:
            An Config instance.
        """
        cfg = Config._parse_yaml(data)
        noc_cfg = Config._parse_noc(cfg)
        expose_cfg = Config._parse_expose(cfg)
        pools_cfg = Config._parse_pools(cfg)
        services_cfg = Config._parse_services(cfg)
        labs_cfg = Config._parse_labs(cfg)
        # Check services refers to proper pools
        for svc_name in services_cfg:
            if "-" in svc_name:
                _, pool = svc_name.split("-", 1)
                if pool not in pools_cfg:
                    with errors.context(["services", svc_name]):
                        errors.error(f"invalid pool {pool}")
        # Check labs refers to proper pools
        for lab_name, lab in labs_cfg.items():
            with errors.context(["labs", lab_name, "pool"]):
                if lab.pool and lab.pool not in pools_cfg:
                    errors.error(f"unknown pool `{lab.pool}`")
                elif lab.pool and pools_cfg[lab.pool].address.gw is None:
                    p = pools_cfg[lab.pool]
                    p.address.gw = p.subnet.first_free(p.address.iter_used())
        # Die on errors
        errors.check()
        return Config(
            project=cfg.get("project"),
            noc=noc_cfg,
            expose=expose_cfg,
            pools=pools_cfg,
            services=services_cfg,
            labs=labs_cfg,
            cli=CliConfig(),
        )

    @staticmethod
    def default() -> "Config":
        """
        Generate default config.

        Returns:
            An Config instance
        """
        return Config(
            project=None,
            noc=NocConfig.default(),
            expose=ExposeConfig.default(),
            pools={},
            services={},
            labs={},
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

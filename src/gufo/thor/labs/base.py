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
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypedDict, Union

# Third-party modules
import jinja2

from gufo.loader import Loader

# Gufo Thor modules
from ..config import (
    Config,
    LabConfig,
    LabNodeConfig,
    LabNodeSnmpCredentials,
    LabNodeUserCredentials,
)
from ..utils import write_file


@dataclass
class EthIfaceSettings(object):
    """
    Ethernet interface settings.

    Attributes:
        name: Interface name.
        address: IPv4 address.
        description: Interface description.
        is_isis: IS-IS is configured on interface.
        isis_metric: IS-IS metric for interface, if not empty.
    """

    name: str
    address: str
    description: str
    is_isis: bool = False
    isis_metric: Optional[int] = None


class ConfigCtx(TypedDict):
    """
    Config template context.

    Attributes:
        hostname: Hostname, may be empty.
        router_id: router-id, may be empty.
        has_protocols: True, if any of protocols set,
            False otherwise.
        has_isis: IS-IS protocol is configured.
        isis_net: IS-IS network, empty if `has_isis` is False.
        eth_interfaces: List of configured ethernet interfaces.
    """

    hostname: str
    router_id: str
    has_protocols: bool
    has_isis: bool
    isis_net: str
    eth_interfaces: List[EthIfaceSettings]
    has_users: bool
    users: List[LabNodeUserCredentials]
    has_snmp: bool
    snmp: List[LabNodeSnmpCredentials]


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
    ) -> Dict[str, Dict[str, Any]]:
        """Get volumes settings."""
        r: Dict[str, Dict[str, Any]] = {}
        for n, link in enumerate(lab_config.links):
            if node_config.name in {link.node_a, link.node_z}:
                delta = 1 if link.node_a == node_config.name else 2
                addr = link.prefix.network + delta
                r[f"lab-{lab_config.name}-l{n}"] = {
                    "interface_name": f"eth{len(r)}",
                    "ipv4_address": str(addr),
                }
        if node_config.pool_gw and lab_config.pool:
            p_cfg = {
                "interface_name": f"eth{len(r)}",
                "ipv4_address": str(config.pools[lab_config.pool].address.gw),
            }
            r[f"pool-{lab_config.pool}"] = p_cfg
        return r

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

    @classmethod
    def get_eth_interface_name(cls, n: int) -> str:
        """
        Generate name for ethernet interface.

        Args:
            n: Interface number (zero-based)

        Returns:
            interface name
        """
        return f"eth{n}"

    @classmethod
    def get_config_context(
        cls,
        config: Config,
        lab_config: LabConfig,
        node_config: LabNodeConfig,
    ) -> ConfigCtx:
        """
        Get context to render config.

        Args:
            config: Full config.
            lab_config: Full lab config.
            node_config: Current node's config.

        Returns:
            Context to render templates.
        """
        # Filter my links
        my_links = [
            link
            for link in lab_config.links
            if node_config.name in {link.node_a, link.node_z}
        ]
        # Get interfaces
        eth_interfaces: List[EthIfaceSettings] = []
        for link in my_links:
            n_eth = len(eth_interfaces)
            delta = 1 if link.node_a == node_config.name else 2
            addr = (link.prefix.network + delta).to_prefix(link.prefix.mask)
            is_isis = "isis" in link.protocols
            isis_metric: Optional[int] = (
                link.protocols["isis"].metric if is_isis else None
            )
            other_peer = (
                link.node_z if link.node_a == node_config.name else link.node_a
            )
            eth_interfaces.append(
                EthIfaceSettings(
                    name=cls.get_eth_interface_name(n_eth),
                    address=str(addr),
                    description=f"to {other_peer}",
                    is_isis=is_isis,
                    isis_metric=isis_metric,
                )
            )
        # Pool-gw
        if node_config.pool_gw and lab_config.pool:
            lab_pool = config.pools[lab_config.pool]
            addr = (
                lab_pool.subnet.to_prefix(lab_pool.address.gw)
                if lab_pool.address.gw
                else (lab_pool.subnet + 1)
            )
            eth_interfaces.append(
                EthIfaceSettings(
                    name=cls.get_eth_interface_name(len(eth_interfaces)),
                    address=str(addr),
                    description=f"pool {lab_config.pool}",
                    is_isis=False,
                )
            )
        # Get all protocols
        protocols: Set[str] = set()
        for link in my_links:
            for proto in link.protocols:
                protocols.add(proto)
        return {
            "hostname": node_config.name,
            "router_id": str(node_config.router_id)
            if node_config.router_id
            else "",
            "has_protocols": bool(protocols),
            "has_isis": "isis" in protocols,
            "isis_net": (
                node_config.router_id.as_isis_net()
                if "isis" in protocols and node_config.router_id
                else ""
            ),
            "eth_interfaces": eth_interfaces,
            "has_users": bool(node_config.users),
            "users": node_config.users or [],
            "has_snmp": bool(node_config.snmp),
            "snmp": node_config.snmp or [],
        }


loader = Loader[Type[BaseLab]](base="gufo.thor.labs", exclude=("base", "noc"))

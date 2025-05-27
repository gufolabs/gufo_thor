# ---------------------------------------------------------------------
# Gufo Thor: VyOS lab router
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""VyOS lab router."""

# Python modules
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

# Gufo Thor modules
from ..config import Config, LabConfig, LabNodeConfig
from ..labs.base import BaseLab


class VyOSLab(BaseLab):
    """VyOS lab router."""

    name = "vyos"
    image = "afla/vyos"

    def get_compose_volumes(
        self, config: Config, lab_config: LabConfig, node_config: LabNodeConfig
    ) -> List[str]:
        """Generate volumes settings."""
        conf_root = self.get_config_dir(lab_config, node_config)
        conf_path = conf_root / "config.boot"
        if not conf_path.exists():
            self._write_initial_config(conf_path, lab_config, node_config)
        return [f"./{conf_root}:/opt/vyatta/etc/config"]

    def _write_initial_config(
        self,
        conf_path: Path,
        lab_config: LabConfig,
        node_config: LabNodeConfig,
    ) -> None:
        # Filter my links
        my_links = [
            link
            for link in lab_config.links
            if node_config.name in {link.node_a, link.node_z}
        ]
        # Get interfaces
        eth_interfaces = []
        for n_eth, link in enumerate(my_links):
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
                    name=f"eth{n_eth}",
                    address=str(addr),
                    description=f"to {other_peer}",
                    is_isis=is_isis,
                    isis_metric=isis_metric,
                )
            )
        # Get all protocols
        protocols: Set[str] = set()
        for link in my_links:
            for proto in link.protocols:
                protocols.add(proto)
        ctx: Dict[str, Union[str, int, List[Any]]] = {
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
        }
        self.render_file(conf_path, "boot.j2", **ctx)


@dataclass
class EthIfaceSettings(object):
    """Ethernet interface settings."""

    name: str
    address: str
    description: str
    is_isis: bool = False
    isis_metric: Optional[int] = None

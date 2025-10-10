# ---------------------------------------------------------------------
# Gufo Thor: Config tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
import tempfile
from pathlib import Path
from typing import Any, Dict, Union

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.config import (
    Config,
    ExposeConfig,
    IsisLinkProtocolConfig,
    LabConfig,
    LabLinkConfig,
    LabNodeConfig,
    Listen,
    NocConfig,
    PoolAddressConfig,
    PoolConfig,
    ServiceConfig,
    get_sample,
)
from gufo.thor.validator import (
    IPv4Address,
    IPv4Prefix,
    errors,
)

from .utils import isolated_errors, override_errors


@isolated_errors
def test_simple() -> None:
    sample = get_sample("simple")
    cfg = Config.from_yaml(sample)
    assert cfg.noc.tag == "master"
    assert cfg.noc.installation_name == "Unconfigured Installation"
    assert cfg.noc.path is None
    assert cfg.noc.custom is None
    assert cfg.expose.domain_name == "go.getnoc.com"
    assert cfg.expose.web
    assert cfg.expose.web.port == 32777
    assert len(cfg.services) == 3
    assert "web" in cfg.services
    assert "card" in cfg.services
    assert not errors.has_errors()


@pytest.mark.parametrize("sample", ["simple", "common", "lab1"])
@isolated_errors
def test_from_yaml(sample: str) -> None:
    sample = get_sample(sample)
    Config.from_yaml(sample)
    assert not errors.has_errors()


@isolated_errors
def test_nonexistent_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        nonexistent_path = Path(tmp) / "not_exists.yaml"
        with pytest.raises(RuntimeError) as exc_info:
            Config.from_file(nonexistent_path)
        assert "Cannot read file" in exc_info.value.args[0]


@isolated_errors
def test_from_file() -> None:
    sample = get_sample("simple")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.yml"
        with open(path, "w") as fp:
            fp.write(sample)
        cfg = Config.from_file(path)
        assert cfg.noc.tag == "master"
        assert cfg.noc.installation_name == "Unconfigured Installation"
        assert not errors.has_errors()


@isolated_errors
def test_non_dict() -> None:
    with pytest.raises(RuntimeError) as exc_info:
        Config.from_yaml("abc")
    assert exc_info.value.args[0] == "Config must be dict"


@isolated_errors
def test_empty_config() -> None:
    Config.from_yaml("services: [web]")
    assert not errors.has_errors()


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (777, "127.0.0.1:777"),
        ("777", "127.0.0.1:777"),
        ("10.0.0.1:777", "10.0.0.1:777"),
        ({"port": 777}, "127.0.0.1:777"),
        ({"address": "10.0.0.1", "port": 777}, "10.0.0.1:777"),
    ],
)
@isolated_errors
def test_listen_from_dict(
    x: Union[int, str, Dict[str, Any]], expected: str
) -> None:
    listener = Listen.from_dict(x)
    assert str(listener) == expected
    assert not errors.has_errors()


@isolated_errors
def test_listen_no_port_fail() -> None:
    Listen.from_dict({"address": "10.0.0.1"})
    assert errors.has_errors()


@pytest.mark.parametrize(
    ("listen", "container_port", "expected"),
    [("777", "6000", "127.0.0.1:777:6000")],
)
@isolated_errors
def test_listen_compose_port(
    listen: str, container_port: int, expected: str
) -> None:
    x = Listen.from_dict(listen)
    assert x.docker_compose_port(container_port) == expected
    assert not errors.has_errors()


@isolated_errors
def test_noc_config1() -> None:
    cfg = NocConfig.from_dict({"config": {"traceback": {"reverse": False}}})
    assert cfg.config is not None
    assert isinstance(cfg.config, dict)
    assert cfg.config.get("traceback")
    assert cfg.config["traceback"].get("reverse") is False
    assert not errors.has_errors()


@isolated_errors
def test_expose_obsolete_port() -> None:
    cfg = ExposeConfig.from_dict({"port": 1212})
    assert cfg.web is not None
    assert str(cfg.web) == "127.0.0.1:1212"
    assert not errors.has_errors()
    assert not errors.has_errors()


@isolated_errors
def test_expose_default() -> None:
    cfg = ExposeConfig.from_dict({})
    assert cfg.web is not None
    assert str(cfg.web) == "127.0.0.1:32777"
    assert not errors.has_errors()


@isolated_errors
def test_expose_wildcard() -> None:
    cfg = ExposeConfig.from_dict(
        {"domain_name": "test.example.com", "web": {"port": 777}}
    )
    assert cfg.web is not None
    assert str(cfg.web) == "0.0.0.0:777"
    assert not errors.has_errors()


@isolated_errors
def test_expose_mongo() -> None:
    cfg = ExposeConfig.from_dict({"mongo": 27017})
    assert cfg.mongo is not None
    assert str(cfg.mongo) == "127.0.0.1:27017"
    assert not errors.has_errors()


@isolated_errors
def test_expose_postgres() -> None:
    cfg = ExposeConfig.from_dict(
        {"postgres": {"address": "192.168.0.2", "port": 5432}}
    )
    assert cfg.postgres is not None
    assert str(cfg.postgres) == "192.168.0.2:5432"
    assert not errors.has_errors()


@isolated_errors
def test_expose_mtls_ca_cert() -> None:
    ExposeConfig.from_dict({"mtls_ca_cert": "ca.crt"})
    assert errors.has_errors()


@isolated_errors
def test_pool_no_gw() -> None:
    cfg = PoolAddressConfig.from_dict({})
    assert cfg.gw is None
    assert not errors.has_errors()


@isolated_errors
def test_pool_no_syslog() -> None:
    cfg = PoolAddressConfig.from_dict({})
    assert cfg.syslog is None
    assert not errors.has_errors()


@isolated_errors
def test_pool_no_trap() -> None:
    cfg = PoolAddressConfig.from_dict({})
    assert cfg.trap is None
    assert not errors.has_errors()


@isolated_errors
def test_pool_gw() -> None:
    cfg = PoolAddressConfig.from_dict({"gw": "192.168.0.1"})
    assert cfg.gw
    assert isinstance(cfg.gw, IPv4Address)
    assert str(cfg.gw) == "192.168.0.1"
    assert not errors.has_errors()


@isolated_errors
def test_pool_syslog() -> None:
    cfg = PoolAddressConfig.from_dict({"syslog": "192.168.0.2"})
    assert cfg.syslog
    assert isinstance(cfg.syslog, IPv4Address)
    assert str(cfg.syslog) == "192.168.0.2"
    assert not errors.has_errors()


@isolated_errors
def test_pool_trap() -> None:
    cfg = PoolAddressConfig.from_dict({"trap": "192.168.0.3"})
    assert cfg.trap
    assert isinstance(cfg.trap, IPv4Address)
    assert str(cfg.trap) == "192.168.0.3"
    assert not errors.has_errors()


@isolated_errors
def test_pool_all() -> None:
    cfg = PoolAddressConfig.from_dict(
        {"gw": "192.168.0.1", "syslog": "192.168.0.2", "trap": "192.168.0.3"}
    )
    assert cfg.gw
    assert isinstance(cfg.gw, IPv4Address)
    assert str(cfg.gw) == "192.168.0.1"
    assert cfg.syslog
    assert isinstance(cfg.syslog, IPv4Address)
    assert str(cfg.syslog) == "192.168.0.2"
    assert cfg.trap
    assert isinstance(cfg.trap, IPv4Address)
    assert str(cfg.trap) == "192.168.0.3"
    assert not errors.has_errors()


@isolated_errors
def test_pool_clash() -> None:
    PoolAddressConfig.from_dict(
        {
            "gw": "192.168.0.1",
            "syslog": "192.168.0.2",
            "trap": "192.168.0.2",
        }
    )
    assert errors.has_errors()


@isolated_errors
def test_pool_iter_used() -> None:
    cfg = PoolAddressConfig.from_dict(
        {
            "gw": "192.168.0.1",
            "syslog": "192.168.0.2",
            "trap": "192.168.0.3",
        }
    )
    r = list(cfg.iter_used())
    assert len(r) == 3
    for n, a in enumerate(r):
        assert str(a) == f"192.168.0.{n + 1}"


@isolated_errors
def test_pool_config() -> None:
    cfg = PoolConfig.from_dict(
        name="default",
        data={"subnet": "192.168.0.0/24", "address": {"gw": "192.168.0.1"}},
    )
    assert cfg.name == "default"
    assert cfg.subnet
    assert isinstance(cfg.subnet, IPv4Prefix)
    assert str(cfg.subnet) == "192.168.0.0/24"
    assert cfg.address
    assert cfg.address.gw
    assert isinstance(cfg.address.gw, IPv4Address)
    assert str(cfg.address.gw) == "192.168.0.1"
    assert not errors.has_errors()


@isolated_errors
def test_service_config1() -> None:
    cfg = ServiceConfig.from_dict({})
    assert cfg.scale == 1
    assert cfg.tag is None
    assert not errors.has_errors()


@isolated_errors
def test_service_config2() -> None:
    cfg = ServiceConfig.from_dict({"tag": "master", "scale": 5})
    assert cfg.scale == 5
    assert cfg.tag is not None
    assert cfg.tag == "master"
    assert not errors.has_errors()


@isolated_errors
def test_lab_node_config() -> None:
    cfg = LabNodeConfig.from_dict(
        name="r1",
        data={
            "type": "vyos",
            "version": "1.4",
            "router-id": "10.0.0.1",
            "users": [
                {"user": "root", "password": "rootpass"},
                {"user": "op", "password": "oppass"},
            ],
            "snmp": [{"version": "v2c", "community": "hidden"}],
        },
    )
    assert cfg.name == "r1"
    assert cfg.type == "vyos"
    assert cfg.version == "1.4"
    assert isinstance(cfg.router_id, IPv4Address)
    assert str(cfg.router_id) == "10.0.0.1"
    assert len(cfg.users) == 2
    assert len(cfg.snmp) == 1
    assert not errors.has_errors()


@isolated_errors
def test_lab_node_config_fail1() -> None:
    LabNodeConfig.from_dict(name="r1", data={"users": "123"})
    assert errors.has_errors()


@isolated_errors
def test_lab_node_config_fail2() -> None:
    LabNodeConfig.from_dict(name="r1", data={"snmp": "123"})
    assert errors.has_errors()


@isolated_errors
def test_lab_node_config_fail3() -> None:
    LabNodeConfig.from_dict(
        name="r1", data={"snmp": [{"community": "public"}]}
    )
    assert errors.has_errors()


@isolated_errors
def test_lab_node_config_fail4() -> None:
    LabNodeConfig.from_dict(
        name="r1", data={"snmp": [{"community": "public", "version": "7"}]}
    )
    assert errors.has_errors()


@isolated_errors
def test_isis_link_protocol_config1() -> None:
    cfg = IsisLinkProtocolConfig.from_dict({})
    assert cfg.metric is None


@isolated_errors
def test_isis_link_protocol_config2() -> None:
    cfg = IsisLinkProtocolConfig.from_dict({"metric": 125})
    assert cfg.metric == 125


@isolated_errors
def test_lab_link_config() -> None:
    cfg = LabLinkConfig.from_dict(
        {
            "prefix": "10.0.0.0/30",
            "node-a": "r1",
            "node-z": "r2",
            "protocols": {"isis": {"metric": 100}},
        }
    )
    assert not errors.has_errors()


@pytest.mark.parametrize("x", ["prefix", "node-a", "node-z"])
@isolated_errors
def test_lab_link_config_missed(x: str) -> None:
    cfg: Dict[str, Any] = {
        "prefix": "10.0.0.0/30",
        "node-a": "r1",
        "node-z": "r2",
        "protocols": {"isis": {"metric": 100}},
    }
    cfg.pop(x)
    LabLinkConfig.from_dict(cfg)
    assert errors.has_errors()


@isolated_errors
def test_lab_link_invalid_protocol() -> None:
    LabLinkConfig.from_dict(
        {
            "prefix": "10.0.0.0/30",
            "node-a": "r1",
            "node-z": "r2",
            "protocols": {"avioncarrier": {}},
        }
    )
    assert errors.has_errors()


@isolated_errors
def test_lab_config() -> None:
    cfg = LabConfig.from_dict(
        name="lab1",
        data={
            "pool": "vyos",
            "nodes": {
                "r1": {
                    "type": "vyos",
                    "version": "1.4",
                    "router-id": "10.0.0.1",
                    "pool-gw": True,
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
                "r2": {
                    "type": "vyos",
                    "version": "1.4",
                    "router-id": "10.0.0.2",
                    "pool-gw": False,
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
            },
            "links": [
                {
                    "prefix": "10.0.1.0/30",
                    "node-a": "r1",
                    "node-z": "r2",
                    "protocols": {"isis": {"metric": 100}},
                }
            ],
        },
    )
    assert not errors.has_errors()
    assert cfg.name == "lab1"
    assert cfg.pool == "vyos"
    assert len(cfg.nodes) == 2
    assert len(cfg.links) == 1


@isolated_errors
def test_lab_config_pool_gw_duplicate_fail() -> None:
    LabConfig.from_dict(
        name="vyos",
        data={
            "pool": "vyos",
            "nodes": {
                "r1": {
                    "type": "vyos",
                    "version": "1.4",
                    "router-id": "10.0.0.1",
                    "pool-gw": True,
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
                "r2": {
                    "type": "vyos",
                    "version": "1.4",
                    "router-id": "10.0.0.2",
                    "pool-gw": True,  # <-- duplicate
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
            },
            "links": [
                {
                    "prefix": "10.0.1.0/30",
                    "node-a": "r1",
                    "node-z": "r2",
                    "protocols": {"isis": {"metric": 100}},
                }
            ],
        },
    )
    assert errors.has_errors()


@isolated_errors
def test_lab_config_no_pool_gw_fail() -> None:
    LabConfig.from_dict(
        name="vyos",
        data={
            "pool": "vyos",
            "nodes": {
                "r1": {
                    "type": "vyos",
                    "version": "1.4",
                    "router-id": "10.0.0.1",
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
                "r2": {
                    "type": "vyos",
                    "version": "1.4",
                    "router-id": "10.0.0.2",
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
            },
            "links": [
                {
                    "prefix": "10.0.1.0/30",
                    "node-a": "r1",
                    "node-z": "r2",
                    "protocols": {"isis": {"metric": 100}},
                }
            ],
        },
    )
    assert errors.has_errors()


@isolated_errors
def test_lab_config_duplicated_router_id() -> None:
    cfg = LabConfig.from_dict(
        name="vyos",
        data={
            "pool": "vyos",
            "nodes": {
                "r1": {
                    "type": "vyos",
                    "version": "1.4",
                    "pool_gw": True,
                    "router-id": "10.0.0.1",
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
                "r2": {
                    "type": "vyos",
                    "version": "1.4",
                    "router-id": "10.0.0.1",
                    "users": [{"user": "vy1", "password": "secret1"}],
                    "snmp": [{"version": "v2c", "community": "public1"}],
                },
            },
            "links": [
                {
                    "prefix": "10.0.1.0/30",
                    "node-a": "r1",
                    "node-z": "r2",
                    "protocols": {"isis": {"metric": 100}},
                }
            ],
        },
    )
    cfg.check()
    assert errors.has_errors()


@isolated_errors
def test_config_default() -> None:
    Config.default()


# Force `invalid pool` error
CFG_SERVICE_INVALID_POOL = """
services: [discovery-default]
"""
# Lab in invalid pool
CFG_LAB_INVALID_POOL = """
labs:
  lab1:
    pool: default
"""
# Services must be dict or list
CFG_SERVICES_INT = """
services: 42
"""
# Lab must be dict
CFG_LAB_MUST_BE_DICT = """
services: [web]
labs: [42]
"""
# Pools must be dict
CFG_POOLS_INT = """
pools: 42
services: [web]
"""


@pytest.mark.parametrize(
    "config",
    [
        CFG_SERVICE_INVALID_POOL,
        CFG_LAB_INVALID_POOL,
        CFG_SERVICES_INT,
        CFG_POOLS_INT,
        CFG_LAB_MUST_BE_DICT,
    ],
)
@isolated_errors
def test_config_errors(config: str) -> None:
    with pytest.raises(RuntimeError):
        Config.from_yaml(config)


CFG_AUTO_ASSIGN_POOL_GW = """
pools:
  vyos:
    subnet: 10.0.2.0/24
services: [ping-vyos]
labs:
  lab1:
    pool: vyos
    nodes:
      r1:
        type: vyos
        version: "1.4"
        router-id: 10.0.0.1
        pool-gw: true
        users:
          - user: vy1
            password: secret1
        snmp:
          - version: v2c
            community: public1
      r2:
        type: vyos
        version: "1.4"
        router-id: 10.0.0.2
        users:
          - user: vy2
            password: secret2
        snmp:
          - version: v2c
            community: public2
"""


@isolated_errors
def test_config_auto_assign_pool_gw() -> None:
    cfg = Config.from_yaml(CFG_AUTO_ASSIGN_POOL_GW)
    assert not errors.has_errors()
    assert "lab1" in cfg.labs
    assert "vyos" in cfg.pools
    assert cfg.pools["vyos"].address.gw is not None
    assert isinstance(cfg.pools["vyos"].address.gw, IPv4Address)
    assert str(cfg.pools["vyos"].address.gw) == "10.0.2.1"


CFG_SERVICES_DICT = """
services:
    web:
        scale: 15
"""


@isolated_errors
def test_config_services_dict() -> None:
    cfg = Config.from_yaml(CFG_SERVICES_DICT)
    assert not errors.has_errors()
    assert "web" in cfg.services
    assert cfg.services["web"].scale == 15

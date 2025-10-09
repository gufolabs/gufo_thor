# ---------------------------------------------------------------------
# Gufo Thor: IP tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import Iterable, Optional

# Third party modules
import pytest

# Gufo Thor modules
from gufo.thor.ip import DEFAULT, DEFAULT_PREFIX, IPv4Address, IPv4Prefix


def test_ipv4_invalid_address() -> None:
    with pytest.raises(ValueError):
        IPv4Address("1.2.3.4.5")


def test_ipv4_str() -> None:
    addr = "127.0.0.1"
    ip = IPv4Address(addr)
    assert str(ip) == addr


def test_ipv4_repr() -> None:
    addr = "127.0.0.1"
    ip = IPv4Address(addr)
    assert repr(ip).startswith(f"<IPv4Address {addr} at 0x")


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [("127.0.0.1", "127.0.0.1", True), ("127.0.0.1", "127.0.0.2", False)],
)
def test_ipv4_hash(x: str, y: str, expected: bool) -> None:
    h1 = hash(IPv4Address(x))
    h2 = hash(IPv4Address(y))
    r = h1 == h2
    assert r is expected


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.1", "127.0.0.2", False),
        ("127.0.0.1", "127.0.0.1", True),
    ],
)
def test_ipv4_eq(x: str, y: str, expected: bool) -> None:
    ipx = IPv4Address(x)
    ipy = IPv4Address(y)
    r = ipx == ipy
    assert r is expected


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        ("127.0.0.1", 0x7F000001),
        ("10.0.0.2", 0x0A000002),
    ],
)
def test_ipv4_int(x: str, expected: int) -> None:
    ipx = IPv4Address(x)
    assert int(ipx) == expected


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (0x7F000001, "127.0.0.1"),
        (0x0A000002, "10.0.0.2"),
    ],
)
def test_ipv4_from_int(x: int, expected: str) -> None:
    ipx = IPv4Address.from_int(x)
    assert isinstance(ipx, IPv4Address)
    ipy = IPv4Address(expected)
    assert ipx == ipy


def test_ipv4_default() -> None:
    ip = IPv4Address.default()
    assert isinstance(ip, IPv4Address)
    assert str(ip) == DEFAULT
    assert IPv4Address.default() is not IPv4Address.default()


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.1", 3, "127.0.0.4"),
        ("10.0.255.255", 2, "10.1.0.1"),
    ],
)
def test_ipv4_add(x: str, y: int, expected: str) -> None:
    ip = IPv4Address(x) + y
    assert isinstance(ip, IPv4Address)
    assert str(ip) == expected


@pytest.mark.parametrize(
    ("x", "area", "expected"),
    [
        ("127.0.0.1", 1, "49.0001.1270.0000.0001.00"),
        ("10.0.255.255", 300, "49.0300.0100.0025.5255.00"),
    ],
)
def test_ipv4_as_isis_net(x: str, area: int, expected: str) -> None:
    ip = IPv4Address(x)
    net = ip.as_isis_net(area)
    assert isinstance(net, str)
    assert net == expected


@pytest.mark.parametrize(
    ("x", "mask", "expected"),
    [
        ("127.0.0.0", 8, "127.0.0.0/8"),
        ("172.16.0.0", 12, "172.16.0.0/12"),
    ],
)
def test_ipv4_to_prefix(x: str, mask: int, expected: str) -> None:
    ip = IPv4Address(x)
    prefix = ip.to_prefix(mask)
    assert isinstance(prefix, IPv4Prefix)
    assert str(prefix) == expected


@pytest.mark.parametrize(
    "x", ["127.0.0.1", "10/20/30", "10.0.0.0/-1", "10.0.0.0/33"]
)
def test_ipv4_prefix_invalid(x: str) -> None:
    with pytest.raises(ValueError):
        IPv4Prefix(x)


def test_ipv4_prefix_str() -> None:
    addr = "127.0.0.1/32"
    ip = IPv4Prefix(addr)
    assert str(ip) == addr


def test_ipv4_prefix_repr() -> None:
    prefix = "127.0.0.1/32"
    ip = IPv4Prefix(prefix)
    assert repr(ip).startswith(f"<IPv4Prefix {prefix} at 0x")


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.0/32", "127.0.0.0/32", True),
        ("127.0.0.0/32", "127.0.0.0/30", False),
        ("127.0.0.0/30", "127.0.0.4/30", False),
    ],
)
def test_ipv4_prefix_hash(x: str, y: str, expected: bool) -> None:
    h1 = hash(IPv4Prefix(x))
    h2 = hash(IPv4Prefix(y))
    r = h1 == h2
    assert r is expected


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.1/32", "127.0.0.1/32", True),
        ("127.0.0.0/32", "127.0.0.0/30", False),
        ("127.0.0.0/30", "127.0.0.4/30", False),
    ],
)
def test_ipv4_prefix_eq(x: str, y: str, expected: bool) -> None:
    p1 = IPv4Prefix(x)
    p2 = IPv4Prefix(y)
    r = p1 == p2
    assert r is expected


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        ("10.0.0.0/8", "10.0.0.0"),
        ("172.16.0.0/12", "172.16.0.0"),
        ("192.168.0.0/16", "192.168.0.0"),
    ],
)
def test_ipv4_prefix_network(x: str, expected: str) -> None:
    p1 = IPv4Prefix(x)
    net = p1.network
    assert isinstance(net, IPv4Address)
    assert str(net) == expected


def test_ipv4_prefix_default() -> None:
    p = IPv4Prefix.default()
    assert isinstance(p, IPv4Prefix)
    assert str(p) == DEFAULT_PREFIX
    assert IPv4Prefix.default() is not IPv4Prefix.default()


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.0/30", "127.0.0.0", True),
        ("127.0.0.0/30", "127.0.0.1", True),
        ("127.0.0.0/30", "127.0.0.2", True),
        ("127.0.0.0/30", "127.0.0.3", True),
        ("127.0.0.0/30", "127.0.0.4", False),
    ],
)
def test_ipv4_prefix_contains(x: str, y: str, expected: str) -> None:
    p = IPv4Prefix(x)
    a = IPv4Address(y)
    r = a in p
    assert r is expected


def test_ipv4_prefix_contains_mismatch() -> None:
    p = IPv4Prefix("127.0.0.0/30")
    r = "127.0.0.1" in p
    assert r is False


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.0/30", 4, "127.0.0.4/30"),
        ("10.0.255.252/30", 4, "10.1.0.0/30"),
    ],
)
def test_ipv4_prefix_add(x: str, y: int, expected: str) -> None:
    p = IPv4Prefix(x) + y
    assert isinstance(p, IPv4Prefix)
    assert str(p) == expected


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.0/30", ["127.0.0.2"], "127.0.0.1"),
        ("127.0.0.0/30", ["127.0.0.1"], "127.0.0.2"),
        ("127.0.0.0/30", ["127.0.0.1", "127.0.0.2"], "127.0.0.3"),
        ("127.0.0.0/30", ["127.0.0.1", "127.0.0.3"], "127.0.0.2"),
        ("127.0.0.0/30", ["127.0.0.1", "127.0.0.2", "127.0.0.3"], None),
    ],
)
def test_ipv4_prefix_first_free(
    x: str, y: Iterable[str], expected: Optional[str]
) -> None:
    p = IPv4Prefix(x)
    r = p.first_free(IPv4Address(a) for a in y)
    if expected is None:
        assert r is None
    else:
        assert str(r) == expected


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("127.0.0.0/30", "10.0.0.0", "10.0.0.0/30"),
        ("10.0.0.0/8", "172.16.0.0", "172.16.0.0/8"),
    ],
)
def test_ipv4_prefix_to_prefix_add(x: str, y: str, expected: str) -> None:
    p = IPv4Prefix(x)
    a = IPv4Address(y)
    r = p.to_prefix(a)
    assert isinstance(r, IPv4Prefix)
    assert str(r) == expected

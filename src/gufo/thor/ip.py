# ---------------------------------------------------------------------
# IP manipulation primitives
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""IP address manipulation primitives."""

# Python modules
from typing import Iterable, Optional

DEFAULT = "0.0.0.0"  # noqa: S104
DEFAULT_PREFIX = "0.0.0.0/0"
MAX_IPV4_MASK = 32


class IPv4Address(object):
    """IPv4 Address."""

    def __init__(self, v: str) -> None:
        parts = [int(x) for x in v.split(".")]
        if len(parts) != 4:  # noqa: PLR2004
            msg = "invalid address"
            raise ValueError(msg)
        self._addr = ".".join(str(x) for x in parts)

    def __str__(self) -> str:
        """Convert to str."""
        return self._addr

    def __repr__(self) -> str:
        """repr() implementation."""
        return f"<{self.__class__.__name__} {self._addr} at 0x{id(self):x}>"

    def __int__(self) -> int:
        """Convert to integer."""
        v = 0
        for p in self._addr.split("."):
            v = (v << 8) + int(p)
        return v

    def __add__(self, v: int) -> "IPv4Address":
        """Add integer value to address."""
        return IPv4Address.from_int(int(self) + v)

    @classmethod
    def from_int(cls, v: int) -> "IPv4Address":
        """Convert integer to IP address."""
        return IPv4Address(
            ".".join(
                str(x)
                for x in (
                    (v >> 24) & 0xFF,
                    (v >> 16) & 0xFF,
                    (v >> 8) & 0xFF,
                    v & 0xFF,
                )
            )
        )

    @staticmethod
    def default() -> "IPv4Address":
        """Get default IPv4 address."""
        return IPv4Address(DEFAULT)

    def as_isis_net(self, /, area: int = 1) -> str:
        """
        Convert ip address to ISIS network.

        Args:
            area: ISIS area.

        Returns:
            ISIS network.
        """
        n = "".join(f"{int(x):03d}" for x in self._addr.split("."))
        return f"49.{area:04d}.{n[:4]}.{n[4:8]}.{n[8:]}.00"

    def to_prefix(self, mask: int) -> "IPv4Prefix":
        """
        Convert address to prefix.

        Args:
            mask: Prefix mask.

        Returns:
            Resulting prefix.
        """
        return IPv4Prefix(f"{self._addr}/{mask}")


class IPv4Prefix(object):
    """IPv4 Prefix."""

    def __init__(self, v: str) -> None:
        try:
            n, m = v.split("/")
        except ValueError as e:
            msg = "invalid prefix"
            raise ValueError(msg) from e
        self._addr = IPv4Address(n)
        mask = int(m)
        if mask < 0 or mask > MAX_IPV4_MASK:
            msg = "invalid mask"
            raise ValueError(msg)
        self._mask = mask

    def __str__(self) -> str:
        """Convert to str."""
        return f"{self._addr!s}/{self.mask}"

    def __repr__(self) -> str:
        """repr() implementation."""
        cname = self.__class__.__name__
        return f"<{cname} {self._addr!s}/{self.mask} at 0x{id(self):x}>"

    @property
    def network(self) -> IPv4Address:
        """Get network part of prefix."""
        return self._addr

    @property
    def mask(self) -> int:
        """Get mask of prefix."""
        return self._mask

    @staticmethod
    def default() -> "IPv4Prefix":
        """Get default IPv4 address."""
        return IPv4Prefix(DEFAULT_PREFIX)

    def __add__(self, v: int) -> "IPv4Prefix":
        """Add integer value to prefix."""
        new_net = self.network + v
        return IPv4Prefix(f"{new_net!s}/{self.mask}")

    def first_free(self, used: Iterable[IPv4Address]) -> Optional[IPv4Address]:
        """
        Find first free address in prefix.

        Args:
            used: Iterable of used IP addresses.

        Returns:
            First free address, None if no free addresses.
        """
        exclude = set(used)
        c = self._addr + 1  # @todo: Separate handing for /31 networks
        while c in exclude:
            c += 1
        return c

    def to_prefix(self, addr: IPv4Address) -> "IPv4Prefix":
        """Add mask to address."""
        return IPv4Prefix(f"{addr}/{self._mask}")

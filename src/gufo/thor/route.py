# ---------------------------------------------------------------------
# Gufo Thor: HTTP route
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""HTTP route definition."""

# Python Modules
from dataclasses import dataclass


@dataclass
class Route:
    """
    Route configuration.

    Attributes:
        name: Service name.
        prefix: HTTP prefix.
        disable_auth: Disable external authorization.
        prefix_rewrite: Rewrite prefix, if set.
        redirect_to: Redirect to path, if matched.
        no_cache: Add headers which disable caching.
        is_service: Expose to `clusters` section.
    """

    name: str
    prefix: str
    disable_auth: bool
    prefix_rewrite: str | None = None
    redirect_to: str | None = None
    no_cache: bool = False
    is_service: bool = True

    @property
    def cluster(self) -> str:
        """Get cluster name."""
        return f"{self.name}_cluster"

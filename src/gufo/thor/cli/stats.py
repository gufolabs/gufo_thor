# ---------------------------------------------------------------------
# Gufo Thor: stats command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Show container statistics."""

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command("stats", short_help="Show container stats.")
@pass_context
@prepared
def stats(ctx: Context) -> None:
    """Show container statistics.

    Args:
        ctx: CLI execution context.
    """
    if not docker.stats():
        ctx.die("Failed to show container statistics.")

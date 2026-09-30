# ---------------------------------------------------------------------
# Gufo Thor: restart command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Restart one or more services."""

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("restart", short_help="Restart services.")
@click.argument("services", nargs=-1, required=True)
@pass_context
def restart(ctx: Context, services: tuple[str, ...]) -> None:
    """Restart one or more services.

    Args:
        ctx: CLI execution context.
        services: Service names.
    """
    ctx.prepare()
    if not docker.restart(*services):
        ctx.die("Failed to restart services.")

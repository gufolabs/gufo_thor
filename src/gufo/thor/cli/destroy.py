# ---------------------------------------------------------------------
# Gufo Thor: destroy command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Destroy the Thor installation."""

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command(
    "destroy", short_help="Destroy installation and free resources."
)
@click.option("--yes", is_flag=True, help="Skip confirmation.")
@pass_context
@prepared
def destroy(ctx: Context, yes: bool) -> None:
    """Destroy the installation and its data.

    Args:
        ctx: CLI execution context.
        yes: Execute without confirmation.
    """
    if not yes and not click.confirm(
        "Destroy installation? All data will be lost!", default=False
    ):
        ctx.die("Destroy cancelled by user.")
    if not docker.destroy():
        ctx.die("Failed to destroy the NOC installation.")

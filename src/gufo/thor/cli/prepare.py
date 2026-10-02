# ---------------------------------------------------------------------
# Gufo Thor: prepare command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Prepare NOC service configuration."""

# Third-party modules
import click

# Gufo Thor modules
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command("prepare", short_help="Prepare services configuration.")
@pass_context
@prepared
def prepare(ctx: Context) -> None:
    """Prepare NOC services configuration.

    Args:
        ctx: CLI execution context.
    """

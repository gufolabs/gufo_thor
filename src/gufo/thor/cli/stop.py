# ---------------------------------------------------------------------
# Gufo Thor: stop command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Stop NOC containers."""

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("stop", short_help="Stop NOC.")
@pass_context
def stop(ctx: Context) -> None:
    """Stop NOC containers.

    Args:
        ctx: CLI execution context.
    """
    if not docker.stop():
        ctx.die("Failed to stop NOC containers.")

# ---------------------------------------------------------------------
# Gufo Thor: pause command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Pause NOC containers."""

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from ..log import logger
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command("pause", short_help="Pause service containers.")
@pass_context
@prepared
def pause(ctx: Context) -> None:
    """Pause NOC containers.

    Args:
        ctx: CLI execution context.
    """
    logger.warning("Pausing containers")
    docker.pause()

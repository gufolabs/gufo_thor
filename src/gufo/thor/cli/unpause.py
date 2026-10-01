# ---------------------------------------------------------------------
# Gufo Thor: unpause command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Resume NOC containers."""

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from ..log import logger
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command("unpause", short_help="Resume service containers.")
@pass_context
@prepared
def unpause(ctx: Context) -> None:
    """Resume NOC containers.

    Args:
        ctx: CLI execution context.
    """
    logger.warning("Resuming containers")
    docker.unpause()

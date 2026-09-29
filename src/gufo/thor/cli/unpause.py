# -----------------------------------------------------------------------
"""Resume NOC containers."""
# unpause command
# -----------------------------------------------------------------------

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from ..log import logger
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("unpause", short_help="Resume service containers.")
@pass_context
def unpause(ctx: Context) -> None:
    """Resume NOC containers.

    Args:
        ctx: CLI execution context.
    """
    ctx.prepare()
    logger.warning("Resuming containers")
    docker.unpause()

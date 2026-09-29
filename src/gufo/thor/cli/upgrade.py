# -----------------------------------------------------------------------
"""Update NOC images."""
# upgrade command
# -----------------------------------------------------------------------

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from ..log import logger
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("upgrade", short_help="Update NOC.")
@pass_context
def upgrade(ctx: Context) -> None:
    """Pull updated images for NOC.

    Args:
        ctx: CLI execution context.
    """
    ctx.prepare()
    logger.warning("Cleaning containers")
    docker.down()
    logger.warning("Pulling new images")
    if not docker.pull():
        ctx.die("Failed to pull Compose images.")
    logger.warning("Running migrate")

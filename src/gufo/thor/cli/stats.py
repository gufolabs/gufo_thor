# -----------------------------------------------------------------------
"""Show container statistics."""
# stats command
# -----------------------------------------------------------------------

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("stats", short_help="Show container stats.")
@pass_context
def stats(ctx: Context) -> None:
    """Show container statistics.

    Args:
        ctx: CLI execution context.
    """
    ctx.prepare()
    if not docker.stats():
        ctx.die("Failed to show container statistics.")

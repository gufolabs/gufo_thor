# -----------------------------------------------------------------------
"""Prepare NOC service configuration."""
# prepare command
# -----------------------------------------------------------------------

# Third-party modules
import click

# Gufo Thor modules
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("prepare", short_help="Prepare services configuration.")
@pass_context
def prepare(ctx: Context) -> None:
    """Prepare NOC services configuration.

    Args:
        ctx: CLI execution context.
    """
    ctx.prepare()

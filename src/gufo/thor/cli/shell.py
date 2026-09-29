# -----------------------------------------------------------------------
"""Run the NOC shell."""
# shell command
# -----------------------------------------------------------------------

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("shell", short_help="Run NOC shell.")
@pass_context
def shell(ctx: Context) -> None:
    """Run the NOC shell.

    Args:
        ctx: CLI execution context.
    """
    ctx.prepare()
    if not docker.shell():
        ctx.die("Failed to start the NOC shell.")

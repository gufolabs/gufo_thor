# -----------------------------------------------------------------------
"""Show logs for one or more services."""
# logs command
# -----------------------------------------------------------------------

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("logs", short_help="Show process logs.")
@click.option("-f", "--follow", is_flag=True, help="Follow logs.")
@click.argument("services", nargs=-1, required=True)
@pass_context
def logs(ctx: Context, follow: bool, services: tuple[str, ...]) -> None:
    """Show logs for one or more services.

    Args:
        ctx: CLI execution context.
        follow: Continue streaming log output.
        services: Service names.
    """
    ctx.prepare()
    if not docker.logs(*services, _follow=follow):
        ctx.die("Failed to show service logs.")

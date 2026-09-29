# -----------------------------------------------------------------------
# version command
# -----------------------------------------------------------------------
# Copyright (C) 2015-2026 Gufo Labs
# See LICENSE.md for details
# -----------------------------------------------------------------------
"""Show the Gufo Thor version."""

# Third-party modules
import click

# Gufo Thor modules
from .. import __version__
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("version", short_help="Show Gufo Thor version.")
@pass_context
def version(ctx: Context) -> None:
    """Print the Gufo Thor version.

    Args:
        ctx: CLI execution context.
    """
    ctx.print(f"Gufo Thor {__version__}")

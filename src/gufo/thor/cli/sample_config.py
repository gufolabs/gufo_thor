# ---------------------------------------------------------------------
# Gufo Thor: sample-config command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Generate sample Thor configuration."""

# Python modules
import os
from pathlib import Path

# Third-party modules
import click

# Gufo Thor modules
from ..config import get_sample
from ..log import logger
from .base import Context, entrypoint, pass_context


@entrypoint
@click.command("sample-config", short_help="Generate sample config.")
@click.option(
    "-t",
    "--template",
    default="simple",
    show_default=True,
    help="Select sample config template.",
)
@pass_context
def sample_config(ctx: Context, template: str) -> None:
    """Generate a sample Thor configuration file.

    Args:
        ctx: CLI execution context.
        template: Sample configuration template name.
    """
    path = Path("thor.yml")
    if os.path.exists(path):
        ctx.die(f"{path} already exists.")
    logger.warning("Writing %s", path)
    path.write_text(get_sample(template))

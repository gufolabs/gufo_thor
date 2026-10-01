# ---------------------------------------------------------------------
# Gufo Thor: up command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Prepare and start NOC."""

# Python modules
import contextlib
import webbrowser

# Third-party modules
import click

# Gufo Thor modules
from ..config import config
from ..docker import docker
from ..log import logger
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command("up", short_help="Set up and launch NOC.")
@click.option("--migrate", is_flag=True, help="Run migrations.")
@click.option("--no-migrate", is_flag=True, help="Skip migrations on run.")
@pass_context
@prepared
def up(ctx: Context, migrate: bool, no_migrate: bool) -> None:
    """Prepare and start NOC.

    Args:
        ctx: CLI execution context.
        migrate: Force migrations to run.
        no_migrate: Skip migrations.
    """
    if migrate and no_migrate:
        ctx.die("Cannot use --migrate and --no-migrate together.")
    if migrate:
        config.noc.migrate = True
    elif no_migrate:
        config.noc.migrate = False
    if not docker.up():
        ctx.die("Failed to start NOC containers.")
    url = config.get_ui_url()
    logger.warning("To access NOC user interface open %s", url)
    if config.expose.open_browser:
        logger.warning("Starting browser")
        with contextlib.suppress(Exception):
            webbrowser.open(url)

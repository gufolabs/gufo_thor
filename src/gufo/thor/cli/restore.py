# ---------------------------------------------------------------------
# Gufo Thor: restore command
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Restore NOC databases from a local backup."""

# Third-party modules
import click

# Gufo Thor modules
from ..backup.restore import restore as run_restore
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command("restore", short_help="Restore NOC databases.")
@click.argument("name")
@click.option("--postgres", is_flag=True, help="Restore PostgreSQL.")
@click.option("--mongo", is_flag=True, help="Restore MongoDB.")
@click.option("--clickhouse", is_flag=True, help="Restore ClickHouse.")
@pass_context
@prepared
def restore(
    ctx: Context,
    name: str,
    postgres: bool,
    mongo: bool,
    clickhouse: bool,
) -> None:
    """Restore all available database dumps or selected services.

    Args:
        ctx: CLI execution context.
        name: Backup directory name.
        postgres: Restore the PostgreSQL service.
        mongo: Restore the MongoDB service.
        clickhouse: Restore the ClickHouse service.
    """
    items = [
        service
        for service, selected in (
            ("postgres", postgres),
            ("mongo", mongo),
            ("clickhouse", clickhouse),
        )
        if selected
    ]
    try:
        run_restore(name, items or None)
    except (NotImplementedError, OSError, RuntimeError, ValueError) as e:
        ctx.die(f"Failed to restore backup: {e}")
    ctx.print(f"Restored backup: {name}")

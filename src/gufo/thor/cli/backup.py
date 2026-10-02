# ---------------------------------------------------------------------
# Gufo Thor: backup commands
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""Create and list database backups."""

# Third-party modules
import click

# Gufo Thor modules
from ..backup.backup import backup as run_backup
from ..backup.ls import list_backups
from ..utils import humanize_size, humanize_time
from .base import Context, entrypoint, pass_context, prepared


@click.group("backup", short_help="Create and list NOC backups.")
def backup_group() -> None:
    """Create and list database backups."""


@backup_group.command("create", short_help="Create a database backup.")
@click.argument("name", required=False)
@click.option("--postgres", is_flag=True, help="Back up PostgreSQL.")
@click.option("--mongo", is_flag=True, help="Back up MongoDB.")
@click.option("--clickhouse", is_flag=True, help="Back up ClickHouse.")
@pass_context
@prepared
def create(
    ctx: Context,
    name: str | None,
    postgres: bool,
    mongo: bool,
    clickhouse: bool,
) -> None:
    """Create backups for all supported services or selected services.

    Args:
        ctx: CLI execution context.
        name: Backup directory name.
        postgres: Back up the PostgreSQL service.
        mongo: Back up the MongoDB service.
        clickhouse: Back up the ClickHouse service.
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
        info = run_backup(items or None, name=name)
    except (NotImplementedError, OSError, RuntimeError, ValueError) as e:
        ctx.die(f"Failed to create backup: {e}")
    ctx.print("Backup summary")
    summary = [("Name", info.name)]
    if info.postgres_size is not None:
        summary.append(("Postgres size", humanize_size(info.postgres_size)))
    if info.mongo_size is not None:
        summary.append(("Mongo size", humanize_size(info.mongo_size)))
    if info.clickhouse_size is not None:
        summary.append(
            ("ClickHouse size", humanize_size(info.clickhouse_size))
        )
    total_size = sum(
        size or 0
        for size in (
            info.postgres_size,
            info.mongo_size,
            info.clickhouse_size,
        )
    )
    summary.append(("Total size", humanize_size(total_size)))
    label_width = max(len(label) for label, _ in summary)
    for label, value in summary:
        ctx.print(f"{label:<{label_width}}: {value}")


@backup_group.command("ls", short_help="List database backups.")
@pass_context
def ls(ctx: Context) -> None:
    """List backups sorted by creation timestamp, newest first.

    Args:
        ctx: CLI execution context.
    """
    headers = (
        "name",
        "timestamp",
        "duration",
        "postgres size",
        "mongo size",
        "clickhouse size",
        "total size",
    )
    alignments = ("<", "<", "<", ">", ">", ">", ">")
    rows: list[tuple[str, ...]] = []
    for info in list_backups():
        sizes = (
            info.postgres_size,
            info.mongo_size,
            info.clickhouse_size,
        )
        rows.append(
            (
                info.name,
                info.ts.strftime("%Y-%m-%d %H:%M:%S"),
                humanize_time(info.duration)
                if info.duration is not None
                else "-",
                humanize_size(info.postgres_size)
                if info.postgres_size is not None
                else "-",
                humanize_size(info.mongo_size)
                if info.mongo_size is not None
                else "-",
                humanize_size(info.clickhouse_size)
                if info.clickhouse_size is not None
                else "-",
                humanize_size(sum(size or 0 for size in sizes)),
            )
        )
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [
            max(width, len(value))
            for width, value in zip(widths, row, strict=True)
        ]
    ctx.print(
        " | ".join(
            f"{header:{alignment}{width}}"
            for header, alignment, width in zip(
                headers, alignments, widths, strict=True
            )
        )
    )
    ctx.print("-+-".join("-" * width for width in widths))
    for row in rows:
        ctx.print(
            " | ".join(
                f"{value:{alignment}{width}}"
                for value, alignment, width in zip(
                    row, alignments, widths, strict=True
                )
            )
        )


backup = entrypoint(backup_group)

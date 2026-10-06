# ---------------------------------------------------------------------
# Gufo Thor: migrate MongoDB FCV command
# ---------------------------------------------------------------------
# Copyright (C) 2026, Gufo Labs
# ---------------------------------------------------------------------
"""Migrate MongoDB to the FCV required by the configured NOC version."""

# Python modules
import time

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from ..images import LEGACY_MONGO_FCV
from ..migrate.mongo import iter_intermediate_fcv, migrate_fcv
from ..state import state
from .base import Context, entrypoint, pass_context, prepared


@entrypoint
@click.command("migrate-mongo", short_help="Migrate MongoDB FCV.")
@pass_context
@prepared
def migrate_mongo(ctx: Context) -> None:
    """Migrate MongoDB FCV one supported version at a time.

    Args:
        ctx: CLI execution context.
    """
    if docker.is_service_running("mongo"):
        ctx.die(
            "MongoDB container is running. "
            "Stop it before migrating MongoDB FCV."
        )
    started_at = time.monotonic()
    current_fcv = state.mongo_fcv or LEGACY_MONGO_FCV
    try:
        for target_fcv in iter_intermediate_fcv():
            ctx.print(f"Migrating MongoFCV {current_fcv} -> {target_fcv}")
            migrate_fcv(target_fcv)
            current_fcv = target_fcv
    except RuntimeError as e:
        ctx.die(str(e))
    elapsed = time.monotonic() - started_at
    ctx.print(f"Migration done in {elapsed:.2f}sec")

# ---------------------------------------------------------------------
# Gufo Thor: Mongo Migrations
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""MongoDB migration utilities for Gufo Thor."""

# Python modules
from collections.abc import Iterable

# Gufo Thor modules
from ..docker import docker
from ..images import LEGACY_MONGO_FCV, get_version_settings
from ..state import state
from ..utils import split_version

FCV_IMAGES = {
    "4.4": "mongo:4.4",
    "5.0": "mongo:5.0",
    "6.0": "mongo:6.0",
    "7.0": "mongo:7.0",
    "8.0": "mongo:8.0",
    "8.2": "mongo:8.2",
    "8.3": "mongo:8.3",
    "9.0": "mongo:9.0",
}


def iter_intermediate_fcv() -> Iterable[str]:
    """Iterate over FCV values required to reach the target version.

    The current FCV is excluded and the target FCV is included. Only FCV
    values with a corresponding MongoDB image in :data:`FCV_IMAGES` are
    returned.

    Returns:
        An iterator over intermediate FCV values in ascending order.
    """
    current = split_version(state.mongo_fcv or LEGACY_MONGO_FCV)
    target = split_version(get_version_settings().target_mongo_fcv)
    for fcv in sorted(split_version(v) for v in FCV_IMAGES):
        if fcv > target:
            return
        if fcv > current:
            yield ".".join(str(x) for x in fcv)


def migrate_fcv(target_fcv: str) -> None:
    """Migrate MongoDB to the requested FCV using its matching image.

    Args:
        target_fcv: FCV to set. It must have a matching image in
            :data:`FCV_IMAGES`.

    Raises:
        RuntimeError: If the FCV is unsupported or MongoDB migration fails.
    """
    image = FCV_IMAGES.get(target_fcv)
    if image is None:
        raise RuntimeError(f"Unsupported MongoDB FCV {target_fcv}")
    current_fcv = state.mongo_fcv or LEGACY_MONGO_FCV
    next_fcv = next(
        (
            fcv
            for fcv in sorted(FCV_IMAGES, key=split_version)
            if split_version(fcv) > split_version(current_fcv)
        ),
        None,
    )
    if target_fcv != next_fcv:
        raise RuntimeError(
            f"Cannot migrate MongoDB FCV {current_fcv} to {target_fcv}; "
            f"next FCV is {next_fcv}"
        )
    project_name = docker.compose_project_name
    volume = f"{project_name}_mongo_data"
    confirm = ", confirm: true" if split_version(target_fcv) >= (7, 0) else ""
    command = (
        "set -e; "
        "mongod --fork --logpath /tmp/mongod.log --bind_ip 127.0.0.1; "
        "trap 'mongod --shutdown || true' EXIT; "
        f"mongosh --quiet --eval 'const r = db.adminCommand("
        f'{{setFeatureCompatibilityVersion: "{target_fcv}"'
        f"{confirm}}}); "
        "if (r.ok !== 1) { printjson(r); quit(1); }'"
    )
    if not docker.run(
        "--rm",
        "--volume",
        f"{volume}:/data/db",
        "--user",
        "mongodb",
        "--entrypoint",
        "/bin/bash",
        image,
        "-ec",
        command,
    ):
        raise RuntimeError(f"Failed to migrate MongoDB to FCV {target_fcv}")
    state.mongo_fcv = target_fcv
    state.save()

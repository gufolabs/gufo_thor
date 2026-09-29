# -----------------------------------------------------------------------
"""Run an interactive console for a lab node."""
# console command
# -----------------------------------------------------------------------

# Third-party modules
import click

# Gufo Thor modules
from ..docker import docker
from ..labs.base import BaseLab
from .base import Context, entrypoint, pass_context

NODE_SPEC_PARTS = 2


@entrypoint
@click.command("console", short_help="Run lab console.")
@click.argument("node")
@pass_context
def console(ctx: Context, node: str) -> None:
    """Open the console for a configured lab node.

    Args:
        ctx: CLI execution context.
        node: Lab node in ``<pool>/<name>`` form.
    """
    parts = node.split("/")
    if len(parts) != NODE_SPEC_PARTS:
        ctx.die(
            f"Invalid node specification `{node}`. "
            "`<lab name>/<node name>` expected."
        )
    lab_name, node_name = parts
    config = ctx.config
    lab_cfg = config.labs.get(lab_name)
    if not lab_cfg:
        ctx.die(f"Unknown lab `{lab_name}`")
    node_cfg = lab_cfg.nodes.get(node_name)
    if not node_cfg:
        ctx.die(f"Unknown node {node_name}")
    lab = BaseLab.get(node_cfg.type)
    cargs = lab.get_docker_console_args(config, lab_cfg, node_cfg)
    if not cargs:
        ctx.die("Node doesn't support console")
    container = f"{docker.compose_project_name}-lab-{lab_name}-{node_name}-1"
    command = [
        "exec",
        "-ti",
        *(cargs.args or []),
        container,
        *(cargs.argv or []),
    ]
    if not docker.docker_exec(*command):
        ctx.die("Failed to start the lab node console.")

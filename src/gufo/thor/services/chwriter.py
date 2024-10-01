# ---------------------------------------------------------------------
# Gufo Thor: chwriter service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
chwriter service.

Attributes:
    chwriter: chwriter service singleton.
"""

# Gufo Thor modules
from .clickhouse import clickhouse
from .kafka import kafka
from .migrate import migrate
from .noc import NocService


class ChwriterService(NocService):
    """chwriter service."""

    name = "chwriter"
    dependencies = (clickhouse, kafka, migrate)


chwriter = ChwriterService()

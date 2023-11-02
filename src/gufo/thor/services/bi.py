# ---------------------------------------------------------------------
# Gufo Thor: bi service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
bi service.

Attributes:
    bi: bi service singleton.
"""

# Gufo Thor modules
from .clickhouse import clickhouse
from .noc import NocService


class BiService(NocService):
    """bi service."""

    name = "bi"
    dependencies = (clickhouse,)


bi = BiService()

# ---------------------------------------------------------------------
# Gufo Thor: datasource service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
datasource service.

Attributes:
    datasource: datasource service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class DatasourceService(NocService):
    """datasource service."""

    name = "datasource"


datasource = DatasourceService()

# ---------------------------------------------------------------------
# Gufo Thor: datasource service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class DatasourceService(NocService):
    name = "datasource"


datasource = DatasourceService()

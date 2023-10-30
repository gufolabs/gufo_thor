# ---------------------------------------------------------------------
# Gufo Thor: bi service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .clickhouse import clickhouse
from .noc import NocService


class BiService(NocService):
    name = "bi"
    dependencies = (clickhouse,)


bi = BiService()

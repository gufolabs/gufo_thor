# ---------------------------------------------------------------------
# Gufo Thor: chwriter service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .clickhouse import clickhouse
from .noc import NocService


class ChwriterService(NocService):
    name = "chwriter"
    dependencies = (clickhouse,)


chwriter = ChwriterService()

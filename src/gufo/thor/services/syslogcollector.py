# ---------------------------------------------------------------------
# Gufo Thor: syslogcollector service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
syslogcollector service.

Attributes:
    syslogcollector: syslogcollector service singleton.
"""

# Gufo Thor modules
from .datastream import datastream
from .kafka import kafka
from .migrate import migrate
from .noc import NocService


class SyslogcollectorService(NocService):
    """syslogcollector service."""

    name = "syslogcollector"
    dependencies = (datastream, kafka, migrate)


syslogcollector = SyslogcollectorService()

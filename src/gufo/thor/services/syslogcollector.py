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
from .liftbridge import liftbridge
from .noc import NocService


class SyslogcollectorService(NocService):
    """syslogcollector service."""

    name = "syslogcollector"
    dependencies = (datastream, liftbridge)


syslogcollector = SyslogcollectorService()

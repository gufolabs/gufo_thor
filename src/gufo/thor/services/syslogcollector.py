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
from .noc import NocService


class SyslogcollectorService(NocService):
    name = "syslogcollector"


syslogcollector = SyslogcollectorService()

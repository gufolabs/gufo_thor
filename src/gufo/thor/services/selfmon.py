# ---------------------------------------------------------------------
# Gufo Thor: selfmon service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
selfmon service.

Attributes:
    selfmon: selfmon service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class SelfmonService(NocService):
    name = "selfmon"


selfmon = SelfmonService()

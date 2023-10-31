# ---------------------------------------------------------------------
# Gufo Thor: icqsender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
icqsender service.

Attributes:
    icqsender: icqsender service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class IcqsenderService(NocService):
    name = "icqsender"


icqsender = IcqsenderService()

# ---------------------------------------------------------------------
# Gufo Thor: tgsender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
tgsender service.

Attributes:
    tgsender: tgsender service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class TgsenderService(NocService):
    """tgsender service."""

    name = "tgsender"


tgsender = TgsenderService()

# ---------------------------------------------------------------------
# Gufo Thor: kafkasender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
kafkasender service.

Attributes:
    kafkasender: kafkasender service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class KafkasenderService(NocService):
    """kafkasender service."""

    name = "kafkasender"


kafkasender = KafkasenderService()

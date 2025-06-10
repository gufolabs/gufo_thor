# ---------------------------------------------------------------------
# Gufo Thor: classifier service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
classifier service.

Attributes:
    classifier: classifier service singleton.
"""

# Gufo Thor modules
from .chwriter import chwriter
from .kafka import kafka
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class ClassifierService(NocService):
    """classifier service."""

    name = "classifier"
    dependencies = (chwriter, kafka, migrate, mongo, postgres)
    is_pooled = True
    require_slots = True


classifier = ClassifierService()

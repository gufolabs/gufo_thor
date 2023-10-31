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
from .liftbridge import liftbridge
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class ClassifierService(NocService):
    name = "classifier"
    dependencies = (postgres, mongo, liftbridge)


classifier = ClassifierService()

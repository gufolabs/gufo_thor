# ---------------------------------------------------------------------
# Gufo Thor: datastream service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
datastream service.

Attributes:
    datastream: datastream service singleton.
"""

# Gufo Thor modules
from .mongo import mongo
from .noc import NocService


class DatastreamService(NocService):
    name = "datastream"
    dependencies = (mongo,)


datastream = DatastreamService()

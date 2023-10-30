# ---------------------------------------------------------------------
# Gufo Thor: datastream service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .mongo import mongo
from .noc import NocService


class DatastreamService(NocService):
    name = "datastream"
    dependencies = (mongo,)


datastream = DatastreamService()

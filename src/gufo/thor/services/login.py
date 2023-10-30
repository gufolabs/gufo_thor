# ---------------------------------------------------------------------
# Gufo Thor: login service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class LoginService(NocService):
    name = "login"
    dependencies = (postgres, mongo)


login = LoginService()

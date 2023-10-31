# ---------------------------------------------------------------------
# Gufo Thor: login service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
login service.

Attributes:
    login: login service singleton.
"""

# Gufo Thor modules
from .migrate import migrate
from .mongo import mongo
from .noc import NocService
from .postgres import postgres


class LoginService(NocService):
    name = "login"
    dependencies = (postgres, mongo, migrate)


login = LoginService()

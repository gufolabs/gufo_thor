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
from .liftbridge import liftbridge
from .migrate import migrate
from .mongo import mongo
from .noc import NocHcService
from .postgres import postgres


class LoginService(NocHcService):
    """
    login service.

    Also used as source of static files from nginx.
    """

    name = "login"
    dependencies = (postgres, mongo, migrate, liftbridge)
    allow_scale = True


login = LoginService()

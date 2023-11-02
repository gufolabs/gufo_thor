# ---------------------------------------------------------------------
# Gufo Thor: mailsender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
mailsender service.

Attributes:
    mailsender: mailsender service singleton.
"""

# Gufo Thor modules
from .noc import NocService


class MailsenderService(NocService):
    """mailsender service."""

    name = "mailsender"


mailsender = MailsenderService()

# ---------------------------------------------------------------------
# Gufo Thor: mailsender service
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Gufo Thor modules
from .noc import NocService


class MailsenderService(NocService):
    name = "mailsender"


mailsender = MailsenderService()

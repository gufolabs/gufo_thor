# ---------------------------------------------------------------------
# Gufo Thor: Error classes
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""Error classes."""


class ThorError(BaseException):
    """Base class for errors."""


class CancelExecution(ThorError):
    """Stop execution and exit with error."""

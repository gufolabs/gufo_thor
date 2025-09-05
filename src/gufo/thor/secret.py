# ---------------------------------------------------------------------
# Gufo Thor: Secret management
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------
"""Secret class."""

# Python modules
import secrets
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

# Gufo Thor modules
from .utils import write_file
from .validator import errors

SECRETS_PREFIX = Path("etc", "noc", "secrets")
DEFAULT_SECRETS_LENGTH = 32


class Secret(object):
    """
    Secret.

    Wrapper for managing secrets.

    Arguments:
        name: Secret name.
        config_path: Optional dot-separated path from NOC's config.
    """

    def __init__(self, name: str, config_path: Optional[str] = None) -> None:
        self.name = name
        self._config_path = config_path

    @property
    def path(self) -> Path:
        """Path to file containing secret."""
        return SECRETS_PREFIX / self.name

    @classmethod
    def generate(cls) -> str:
        """Generate new secret."""
        return secrets.token_urlsafe(DEFAULT_SECRETS_LENGTH)

    def ensure_secret(self) -> None:
        """Write secret when necessary."""
        path = self.path
        if not path.exists():
            write_file(path, self.generate())

    def set_secret(self, secret: str) -> None:
        """Set externally known secret."""
        write_file(self.path, secret)

    def check_config(self, cfg: Dict[str, Any]) -> None:
        """
        Check config.

        If secret is set in config, write to secret file and issue warning.
        """

        def path_value(data: Dict[str, Any], path: str) -> Optional[str]:
            if "." not in path:
                v = data.get(path)
                if v is None:
                    return None
                return str(v)
            p, rest = path.split(".", 1)
            d = data.get(p)
            if d:
                return path_value(d, rest)
            return None

        if not self._config_path or not cfg:
            return
        v = path_value(cfg, self._config_path)
        if v is not None:
            with errors.context(self._config_path):
                self.set_secret(v)
                errors.error(
                    "Explicit set of secret in config. Please remove key"
                )

    @classmethod
    def iter_secrets(cls) -> "Iterable[Secret]":
        """Iterate over all secrets."""
        yield secret_key


secret_key = Secret("secret-key", config_path="secret_key")

# ---------------------------------------------------------------------
# Gufo Thor: Secrets check
# ---------------------------------------------------------------------
# Copyright (C) 2022-25, Gufo Labs
# See LICENSE.md for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Dict, Optional, Set

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.secret import SECRETS_PREFIX, Secret
from gufo.thor.validator import errors, override_errors

DEFAULT_SECRET_LEN = 43  # 32 bytes in base64
TEST_SECRET_NAME = "test_secret"


def test_path() -> None:
    with Secret(TEST_SECRET_NAME) as secret:
        assert secret.path == SECRETS_PREFIX / TEST_SECRET_NAME


def test_set_secret() -> None:
    with Secret(TEST_SECRET_NAME) as secret:
        key = secret.generate()
        secret.set_secret(key)
        with open(secret.path) as fp:
            data = fp.read()
            assert data == key


def test_generate_secret() -> None:
    with Secret(TEST_SECRET_NAME) as secret:
        seen: Set[str] = set()
        for _ in range(10):
            s = secret.generate()
            assert len(s) == DEFAULT_SECRET_LEN
            assert s not in seen
            seen.add(s)


def test_ensure_secret() -> None:
    with Secret(TEST_SECRET_NAME) as secret:
        secret.ensure_secret()
        with open(secret.path) as fp:
            data = fp.read()
            assert len(data) == DEFAULT_SECRET_LEN


def test_iter_secrets() -> None:
    for secret in Secret.iter_secrets():
        assert isinstance(secret, Secret)


@pytest.mark.parametrize(
    ("config_path", "data", "has_errors"),
    [
        (None, {"x": "123"}, False),
        ("x", {"x": "123"}, True),
        ("x.y", {"a": "b"}, False),
        ("x.y", {"x": {}}, False),
        ("x.y", {"x": {"a": "b"}}, False),
        ("x.y", {"x": {"y": "b"}}, True),
    ],
)
def test_check_config(
    config_path: Optional[str], data: Dict[str, Any], has_errors: bool
) -> None:
    with (
        Secret(TEST_SECRET_NAME, config_path=config_path) as secret,
        override_errors(),
    ):
        secret.check_config(data)
        assert errors.has_errors() is has_errors

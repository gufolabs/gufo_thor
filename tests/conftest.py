# ---------------------------------------------------------------------
# Gufo Thor: Tests configuration
# ---------------------------------------------------------------------
# Copyright (C) 2024-25, Gufo Labs
# See LICENSE.md for details
# ---------------------------------------------------------------------

# Python modules
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Optional, Tuple

# Third-party modules
import pytest

# Gufo Thor modules
from gufo.thor.artefact import Artefact

_artefacts_tmp_dir: Optional[TemporaryDirectory[str]] = None


def pytest_configure(config: pytest.Config):
    """
    Run before all tests.

    1. Create artefacts temporary base.
    """
    global _artefacts_tmp_dir  # noqa: PLW0603
    # Rebase artefacts
    _artefacts_tmp_dir = TemporaryDirectory()
    Artefact._set_local_base(Path(_artefacts_tmp_dir.name))
    # Write artefacts
    for art, cfg in _iter_artefacts():
        art.write(cfg)


def _iter_artefacts() -> Iterable[Tuple[Artefact, str]]:
    from gufo.thor.services.envoy import envoy_cert, envoy_key, envoy_settings
    from gufo.thor.services.noc import noc_settings

    yield noc_settings, ""
    yield envoy_settings, ""
    yield envoy_cert, ""
    yield envoy_key, ""


def pytest_unconfigure(config: pytest.Config):
    """Run after all tests."""
    global _artefacts_tmp_dir  # noqa: PLW0603
    Artefact._set_local_base()
    if _artefacts_tmp_dir:
        _artefacts_tmp_dir.cleanup()
        _artefacts_tmp_dir = None

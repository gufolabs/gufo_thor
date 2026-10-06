# ---------------------------------------------------------------------
# Gufo Thor: docker-compose target tests
# ---------------------------------------------------------------------
# Copyright (C) 2023-25, Gufo Labs
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# Gufo Thor Modules
from gufo.thor.config import Config, get_sample, with_config
from gufo.thor.state import with_state
from gufo.thor.targets.compose import ComposeTarget

SAMPLES = ["simple", "common", "lab1"]
SAMPLE_IDS = ["simple", "common", "lab1"]


@pytest.mark.parametrize("sample", SAMPLES, ids=SAMPLE_IDS)
def test_render_config(sample: str) -> None:
    t = get_sample(sample)
    with with_config(Config.from_yaml(t)), with_state():
        target = ComposeTarget()
        target.render_config()
        target.prepare()

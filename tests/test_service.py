# ---------------------------------------------------------------------
# Gufo Thor: Service tests
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
import pytest
from gufo.thor.config import Config

# Gufo Thor modules
from gufo.thor.services.base import (
    BaseService,
    ComposeDependsCondition,
    loader,
)
from gufo.thor.services.clickhouse import clickhouse
from gufo.thor.services.consul import consul
from gufo.thor.services.liftbridge import liftbridge
from gufo.thor.services.login import login
from gufo.thor.services.migrate import migrate
from gufo.thor.services.mongo import mongo
from gufo.thor.services.nginx import nginx
from gufo.thor.services.postgres import postgres
from gufo.thor.services.traefik import traefik
from gufo.thor.services.web import web

ALL_SERVICES = set(loader.keys())


@pytest.mark.parametrize(
    ("svc", "expected"),
    [
        (
            "web",
            [
                clickhouse,
                consul,
                liftbridge,
                login,
                migrate,
                mongo,
                nginx,
                postgres,
                traefik,
                web,
            ],
        ),
        (
            "nginx",
            [
                clickhouse,
                consul,
                liftbridge,
                login,
                migrate,
                mongo,
                nginx,
                postgres,
                traefik,
            ],
        ),
    ],
    ids=["web", "nginx"],
)
def test_resolve(svc: str, expected: List[BaseService]) -> None:
    result = BaseService.resolve([svc])
    print(result)
    assert expected == result


@pytest.mark.parametrize("svc", list(loader.keys()))
def test_compose_config(svc: str) -> None:
    config = Config.default()
    s = loader[svc].get_compose_config(config, None)
    assert s


@pytest.mark.parametrize("svc", list(loader.keys()))
def test_compose_healthcheck(svc: str) -> None:
    config = Config.default()
    service = loader[svc]
    cond = service.get_compose_depends_condition(config, None)
    if cond != ComposeDependsCondition.HEALTHY:
        pytest.xfail("No healthcheck configured")
    healthcheck = service.get_compose_healthcheck(config, None)
    assert healthcheck
    assert isinstance(healthcheck, dict)


DEPS_DOT = """digraph {
  sae -> activator
  liftbridge -> activator
  bh
  clickhouse -> bi
  migrate -> card
  postgres -> card
  mongo -> card
  clickhouse -> card
  traefik -> card
  nginx -> card
  migrate -> chwriter
  clickhouse -> chwriter
  liftbridge -> chwriter
  migrate -> classifier
  postgres -> classifier
  mongo -> classifier
  liftbridge -> classifier
  clickhouse
  consul
  migrate -> correlator
  postgres -> correlator
  mongo -> correlator
  liftbridge -> correlator
  datasource
  mongo -> datastream
  traefik -> datastream
  migrate -> discovery
  postgres -> discovery
  mongo -> discovery
  clickhouse -> discovery
  activator -> discovery
  escalator
  grafanads
  icqsender
  kafkasender
  liftbridge
  postgres -> login
  mongo -> login
  migrate -> login
  mailsender
  metrics
  metricscollector
  mib
  postgres -> migrate
  mongo -> migrate
  liftbridge -> migrate
  clickhouse -> migrate
  mongo
  mrt
  mx
  migrate -> nbi
  mongo -> nbi
  postgres -> nbi
  traefik -> nbi
  traefik -> nginx
  login -> nginx
  liftbridge -> ping
  datastream -> ping
  postgres
  migrate -> sae
  postgres -> sae
  mongo -> sae
  migrate -> scheduler
  postgres -> scheduler
  mongo -> scheduler
  migrate -> selfmon
  postgres -> selfmon
  mongo -> selfmon
  datastream -> syslogcollector
  liftbridge -> syslogcollector
  tgsender
  datastream -> topo
  liftbridge -> topo
  consul -> traefik
  datastream -> trapcollector
  liftbridge -> trapcollector
  migrate -> ui
  postgres -> ui
  mongo -> ui
  traefik -> ui
  nginx -> ui
  migrate -> web
  postgres -> web
  mongo -> web
  clickhouse -> web
  traefik -> web
  nginx -> web
  migrate -> worker
  postgres -> worker
  mongo -> worker
  zeroconf
}"""


def test_deps_dot() -> None:
    dot = BaseService.get_deps_dot()
    print(dot)
    assert dot == DEPS_DOT

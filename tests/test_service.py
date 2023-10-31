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
from gufo.thor.services.login import login
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
                login,
                mongo,
                nginx,
                postgres,
                traefik,
                web,
            ],
        ),
        (
            "nginx",
            [consul, login, mongo, nginx, postgres, traefik],
        ),
    ],
    ids=["web", "nginx"],
)
def test_resolve(svc: str, expected: List[BaseService]) -> None:
    result = BaseService.resolve([svc])
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
  postgres -> card
  mongo -> card
  clickhouse -> card
  traefik -> card
  nginx -> card
  clickhouse -> chwriter
  postgres -> classifier
  mongo -> classifier
  liftbridge -> classifier
  clickhouse
  consul
  postgres -> correlator
  mongo -> correlator
  liftbridge -> correlator
  datasource
  mongo -> datastream
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
  mailsender
  metrics
  metricscollector
  mib
  mongo
  mrt
  mx
  nbi
  traefik -> nginx
  login -> nginx
  ping
  postgres
  consul -> registrator
  postgres -> sae
  mongo -> sae
  scheduler
  selfmon
  syslogcollector
  tgsender
  topo
  consul -> traefik
  trapcollector
  ui
  postgres -> web
  mongo -> web
  clickhouse -> web
  traefik -> web
  nginx -> web
  worker
  zeroconf
}"""


def test_deps_dot() -> None:
    dot = BaseService.get_deps_dot()
    print(dot)
    assert dot == DEPS_DOT

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
from gufo.thor.services.auth import auth

# Gufo Thor modules
from gufo.thor.services.base import (
    BaseService,
    ComposeDependsCondition,
    loader,
)
from gufo.thor.services.clickhouse import clickhouse
from gufo.thor.services.consul import consul
from gufo.thor.services.envoy import envoy
from gufo.thor.services.liftbridge import liftbridge
from gufo.thor.services.login import login
from gufo.thor.services.migrate import migrate
from gufo.thor.services.mongo import mongo
from gufo.thor.services.postgres import postgres
from gufo.thor.services.static import static
from gufo.thor.services.web import web
from gufo.thor.services.worker import worker

ALL_SERVICES = sorted(set(loader.keys()))


@pytest.mark.parametrize("svc", ALL_SERVICES)
def test_depends_sorted(svc: str) -> None:
    service = loader[svc]
    if service.dependencies is None:
        pytest.skip("No dependencies")
    x = tuple(sorted(service.dependencies, key=lambda x: x.name))
    assert service.dependencies == x


@pytest.mark.parametrize(
    ("svc", "expected"),
    [
        (
            "web",
            [
                auth,
                clickhouse,
                consul,
                envoy,
                liftbridge,
                login,
                migrate,
                mongo,
                postgres,
                static,
                web,
                worker,
            ],
        ),
        (
            "envoy",
            [
                envoy,
            ],
        ),
    ],
    ids=["web", "envoy"],
)
def test_resolve(svc: str, expected: List[BaseService]) -> None:
    result = BaseService.resolve([svc])
    assert expected == result


@pytest.mark.parametrize("svc", ALL_SERVICES)
def test_compose_config(svc: str) -> None:
    config = Config.default()
    s = loader[svc].get_compose_config(config, None)
    assert s


@pytest.mark.parametrize("svc", ALL_SERVICES)
def test_compose_healthcheck(svc: str) -> None:
    config = Config.default()
    service = loader[svc]
    cond = service.get_compose_depends_condition(config, None)
    if cond != ComposeDependsCondition.HEALTHY:
        pytest.skip("No healthcheck configured")
    healthcheck = service.get_compose_healthcheck(config, None)
    assert healthcheck
    assert isinstance(healthcheck, dict)


@pytest.mark.parametrize("svc", ALL_SERVICES)
def test_envoy_deps(svc: str) -> None:
    config = Config.default()
    service = loader[svc]
    path = service.get_expose_http_prefix(config, None)
    if path:
        assert service.dependencies
        assert (
            envoy in service.dependencies
        ), "Exposes http prefix, must have `envoy` dependency"
    else:
        assert (
            not service.dependencies or envoy not in service.dependencies
        ), "Not exposes http prefix, must not have `envoy` dependency"


@pytest.mark.parametrize("svc", ALL_SERVICES)
def test_migrate_deps(svc: str) -> None:
    if svc == "migrate":
        pytest.skip("migrate service")
    service = loader[svc]
    deps = set(service.iter_dependencies())
    if mongo in deps:
        assert migrate in deps, "Depends on `mongo`, must depend on `migrate`"
    if postgres in deps:
        assert (
            migrate in deps
        ), "Depends on `postgres`, must depend on `migrate`"
    if clickhouse in deps:
        assert (
            migrate in deps
        ), "Depends on `clickhouse`, must depend on `migrate`"
    if liftbridge in deps:
        assert (
            migrate in deps
        ), "Depends on `liftbridge`, must depend on `migrate`"


@pytest.mark.parametrize("svc", ALL_SERVICES)
def test_envoy_http_auth(svc: str) -> None:
    config = Config.default()
    service = loader[svc]
    path = service.get_expose_http_prefix(config, None)
    if service.require_http_auth:
        assert (
            path
        ), "`require_http_auth` must be used only with `expose_http_prefix`"
        assert service.dependencies, "Requires auth, must depend on `auth`"
        assert (
            auth in service.dependencies
        ), "Requires auth, must depend on `auth`"
        if login in service.dependencies:
            assert (
                auth in service.dependencies
            ), "Depends on `login`, must also depends on `auth`"


DEPS_DOT = """digraph {
  liftbridge -> activator
  migrate -> activator
  sae -> activator
  envoy -> auth
  liftbridge -> auth
  migrate -> auth
  mongo -> auth
  auth -> bi
  clickhouse -> bi
  envoy -> bi
  login -> bi
  migrate -> bi
  static -> bi
  auth -> card
  clickhouse -> card
  envoy -> card
  login -> card
  migrate -> card
  mongo -> card
  postgres -> card
  static -> card
  clickhouse -> chwriter
  liftbridge -> chwriter
  migrate -> chwriter
  liftbridge -> classifier
  migrate -> classifier
  mongo -> classifier
  postgres -> classifier
  liftbridge -> correlator
  migrate -> correlator
  mongo -> correlator
  postgres -> correlator
  auth -> datastream
  envoy -> datastream
  migrate -> datastream
  mongo -> datastream
  activator -> discovery
  chwriter -> discovery
  migrate -> discovery
  mongo -> discovery
  postgres -> discovery
  envoy -> login
  migrate -> login
  mongo -> login
  postgres -> login
  static -> login
  clickhouse -> migrate
  consul -> migrate
  liftbridge -> migrate
  mongo -> migrate
  postgres -> migrate
  auth -> nbi
  envoy -> nbi
  migrate -> nbi
  mongo -> nbi
  postgres -> nbi
  datastream -> ping
  liftbridge -> ping
  migrate -> ping
  liftbridge -> runner
  migrate -> runner
  mongo -> runner
  migrate -> sae
  mongo -> sae
  postgres -> sae
  migrate -> scheduler
  mongo -> scheduler
  postgres -> scheduler
  migrate -> selfmon
  mongo -> selfmon
  postgres -> selfmon
  clickhouse -> shell
  migrate -> shell
  mongo -> shell
  postgres -> shell
  worker -> shell
  envoy -> static
  datastream -> syslogcollector
  liftbridge -> syslogcollector
  migrate -> syslogcollector
  datastream -> topo
  liftbridge -> topo
  migrate -> topo
  datastream -> trapcollector
  liftbridge -> trapcollector
  migrate -> trapcollector
  auth -> ui
  envoy -> ui
  login -> ui
  migrate -> ui
  mongo -> ui
  postgres -> ui
  static -> ui
  auth -> web
  clickhouse -> web
  envoy -> web
  login -> web
  migrate -> web
  mongo -> web
  postgres -> web
  static -> web
  worker -> web
  migrate -> worker
  mongo -> worker
  postgres -> worker
}"""


def test_deps_dot() -> None:
    dot = BaseService.get_deps_dot()
    print(dot)
    assert dot == DEPS_DOT

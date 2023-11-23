# ---------------------------------------------------------------------
# Gufo Thor: docker-compose target tests
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# Gufo Thor Modules
from gufo.thor.config import Config, get_sample
from gufo.thor.targets.compose import ComposeTarget

CFG_SIMPLE = """version: '3'
services:
  card:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    - clickhouse
    - traefik
    - nginx
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/card/service.py
    networks:
    - noc
  clickhouse:
    image: yandex/clickhouse-server:latest
    restart: 'no'
    volumes:
    - ./etc/clickhouse-server/:/etc/clickhouse-server
    - ./data/clickhouse:/opt/clickhouse/data
    - ./data/clickhouse/metadata:/opt/clickhouse/metadata
    - ./data/clickhouse/logs:/var/log/clickhouse-server
    networks:
    - noc
    environment:
      SERVICE_8123_NAME: clickhouse
      SERVICE_9000_IGNORE: '1'
      SERVICE_9009_IGNORE: '1'
  consul:
    image: consul:1.15
    restart: 'no'
    networks:
    - noc
    environment:
      SERVICE_IGNORE: '1'
  login:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/login/service.py
    networks:
    - noc
  mongo:
    image: mongo:4.4
    restart: 'no'
    command: --wiredTigerCacheSizeGB 4 --bind_ip_all
    volumes:
    - ./data/mongo:/data/db
    networks:
    - noc
  nginx:
    image: nginx:stable
    restart: 'no'
    depends_on:
    - traefik
    - login
    volumes:
    - ./etc/nginx:/etc/nginx
    networks:
      noc:
        ipv4_address: 172.20.0.100
        aliases:
        - nginx
        - go.getnoc.com
    ports:
    - 32777:443
  postgres:
    image: postgres:16
    restart: 'no'
    volumes:
    - ./data/postgres:/var/lib/postgresql/data
    networks:
    - noc
    environment:
      POSTGRES_DB: noc
      POSTGRES_USER: noc
      POSTGRES_PASSWORD: noc
  traefik:
    image: traefik:1.6
    restart: 'no'
    depends_on:
    - consul
    command: --web --loglevel=INFO --consulcatalog.endpoint=consul:8500 --consulcatalog.prefix=traefik
      --consulcatalog.constraints="tag==backend" --graceTimeout=10s
    volumes:
    - /dev/null:/traefik.toml
    networks:
    - noc
  web:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    - clickhouse
    - traefik
    - nginx
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/web/service.py
    networks:
    - noc
networks:
  noc:
    driver: bridge
"""

CFG_COMMON = """version: '3'
services:
  activator:
    image: noc:master
    restart: 'no'
    depends_on:
    - sae
    - liftbridge
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/activator/service.py
    networks:
    - noc
  card:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    - clickhouse
    - traefik
    - nginx
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/card/service.py
    networks:
    - noc
  classifier:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    - liftbridge
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/classifier/service.py
    networks:
    - noc
  clickhouse:
    image: yandex/clickhouse-server:latest
    restart: 'no'
    volumes:
    - ./etc/clickhouse-server/:/etc/clickhouse-server
    - ./data/clickhouse:/opt/clickhouse/data
    - ./data/clickhouse/metadata:/opt/clickhouse/metadata
    - ./data/clickhouse/logs:/var/log/clickhouse-server
    networks:
    - noc
    environment:
      SERVICE_8123_NAME: clickhouse
      SERVICE_9000_IGNORE: '1'
      SERVICE_9009_IGNORE: '1'
  consul:
    image: consul:1.15
    restart: 'no'
    networks:
    - noc
    environment:
      SERVICE_IGNORE: '1'
  correlator:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    - liftbridge
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/correlator/service.py
    networks:
    - noc
  discovery:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    - clickhouse
    - activator
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/discovery/service.py
    networks:
    - noc
  liftbridge:
    image: liftbridge:v1.9.0
    restart: 'no'
    entrypoint: liftbridge --config /etc/liftbridge.yml
    volumes:
    - ./data/liftbridge:/data/
    - ./etc/liftbridge.yml:/etc/liftbridge.yml
    networks:
    - noc
    environment:
      SERVICE_9292_NAME: liftbridge
  login:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/login/service.py
    networks:
    - noc
  mongo:
    image: mongo:4.4
    restart: 'no'
    command: --wiredTigerCacheSizeGB 4 --bind_ip_all
    volumes:
    - ./data/mongo:/data/db
    networks:
    - noc
  nginx:
    image: nginx:stable
    restart: 'no'
    depends_on:
    - traefik
    - login
    volumes:
    - ./etc/nginx:/etc/nginx
    networks:
      noc:
        ipv4_address: 172.20.0.100
        aliases:
        - nginx
        - go.getnoc.com
    ports:
    - 32777:443
  ping:
    image: noc:master
    restart: 'no'
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/ping/service.py
    networks:
    - noc
  postgres:
    image: postgres:16
    restart: 'no'
    volumes:
    - ./data/postgres:/var/lib/postgresql/data
    networks:
    - noc
    environment:
      POSTGRES_DB: noc
      POSTGRES_USER: noc
      POSTGRES_PASSWORD: noc
  sae:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/sae/service.py
    networks:
    - noc
  traefik:
    image: traefik:1.6
    restart: 'no'
    depends_on:
    - consul
    command: --web --loglevel=INFO --consulcatalog.endpoint=consul:8500 --consulcatalog.prefix=traefik
      --consulcatalog.constraints="tag==backend" --graceTimeout=10s
    volumes:
    - /dev/null:/traefik.toml
    networks:
    - noc
  web:
    image: noc:master
    restart: 'no'
    depends_on:
    - postgres
    - mongo
    - clickhouse
    - traefik
    - nginx
    working_dir: /opt/noc
    command: /usr/local/bin/python3 /opt/noc/services/web/service.py
    networks:
    - noc
networks:
  noc:
    driver: bridge
    ipam:
      config:
      - subnet: 172.20.0.0/24
        gateway: 172.20.0.1
"""


@pytest.mark.parametrize(
    "sample",
    ["simple", "common"],
    ids=["simple", "common"],
)
def test_render_config(sample: str) -> None:
    t = get_sample(sample)
    cfg = Config.from_yaml(t)
    target = ComposeTarget(cfg)
    target.render_config()

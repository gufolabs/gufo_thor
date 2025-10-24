---
hide:
    - navigation
---
# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

To see unreleased changes, please see the [CHANGELOG on the master branch](https://github.com/gufolabs/gufo_thor/blob/master/CHANGELOG.md) guide.

## [Upcoming]

## Fixed

* migrate container no longer pollutes environment of other containers

## Changed

* Configs are deployed using docker's `configs` section. 
* NOC's config are mounted in /etc/noc/settings.yml.
* Move postgres' password to secrets.
* Use `bitnamilegacy` images for kafka.

## Infrastructure

* Use Python 3.14 for devcontainer.
* Codecov integration.
* CodeQL scanning.
* Install security patches into devcontainer.
* Gufo ACME 0.6.0
* IPython 9.4.0
* Jinja2 3.1.6
* Ruff 0.14
* devcontainer: Python debugger settings.

## 0.11.0 - 2025-09-12

## Fixed

* #20: Fix default routes for pool services if pool is not attached to lab.

### Added

* Secrets management.
* Generate unique `secret_key` on first start.

### Changed

* expose.web: listen on all interfaces by default, if domain differs from `go.getnoc.com`.
* Docker container labels `noc.role` and `noc.pool` now are prefixed with `com.gufolabs.`.
* docker-compose.yml: Do not use yaml aliases for healthchecks.

### Infrastructure

* gufo-loader 1.0.4

## 0.10.0 - 2025-06-24

### Fixed

* Do not show trace when docker daemon is not running.

### Added

* mTLS support.
* `expose.mtls_ca_cert` setting.
* `logs` command.
* `stats` command.
* `destroy` command.
* `upgrade` command.
* Show gufo-thor version on startup.
* `noc.role` and `noc.pool` container labels.

### Changed

* Use `exec` to replace process' image when possible.

### Removed

* Old python's docker-compose support.

## 0.9.1 - 2025-06-24

### Fixed

* Use `NoReturn` instead of `Never` for Python 3.9 and 3.10 compatibility.

### Changed

* static: Do not expose config and crashinfo volumes

## 0.9.0 - 2025-06-23

### Added

* Self-signed certificates for domains which don't support CSR Proxy.

## 0.8.0 - 2025-06-10

### Fixed

* CSR Proxy client uses Certifi's root CA list implicitly.

### Added

* Network laboratories.
* Kafka flushes every message on single-node installations.
* `expose.web` setting.
* `expose.mongo` and `expose.postgres` settings.
* `backup` volume.

### Changed

* `expose.port` replaced with `expose.web.port` settings.
* `crashinfo` volume exposed to local filesystem.

### Infrastructure

* Use `ruff` for formatting.
* Move CI lint to separate step.
* Move dependencies from `.requirements/` to `pyproject.toml`.

## 0.7.0 - 2025-01-23

### Fixed

* Do not raise exception when cannot start browser.

### Added

* Unified login support.
* `restart` command.
* `noc.config` section.

### Changed

* `liftbridge` service replaced with `kafka`

## 0.6.0 - 2024-08-05

### Added

* `noc.migrate` config option.
* `gufo-thor --migrate` option.
* `crashinfo` volume.

### Changed

* Do not write `version` attribute to `docker-compose.yml`.
* Do not override the container's `/opt/noc/ui/pkg`.
* `worker` service depends on `liftbridge` and `datastream`.
* `web` service depends on `worker` and `scheduler`.

## 0.5.0 - 2024-04-20

### Added

* `gufo-thor up --no-migrate` option.

### Changed

* `shell` no longer depends on `migrate`.

## 0.4.0 - 2023-12-29

### Added

* `envoy` service.
* `thor.yml`: `noc.theme` parameter.
* `static` service for serving static files.
* `auth` service.

### Changed

* Code streamlining and refactoring.
* Refined service dependencies.
  
### Removed

* `nginx` service.
* `traefik` service.

## 0.3.3 - 2023-12-18

### Fixed

* Fixed ping container capabilities.

### Added

* curl/sh installation script.
* docs: Configuration reference.
* docs: Configuration templates.
* docs: Command Line reference.

### Changed

* docs: Updated installation guide.

## 0.3.2 - 2023-12-10

### Fixed

* Mount consul's config in read/write mode to prevent the permissions changing error.

### Added

* Upgrade instructuons.

## 0.3.1 - 2023-12-10

### Fixed

* `FileNotFoundError` when writing nginx keys.

### Changed

* `write_file` accepts content as `str` and `bytes`.

## 0.3.0 - 2023-11-28

### Added

* config: `project` option.
* config: `service.<name>.scale` option.
* jinja2 templates for configs.
* Perform all migrations and collections loading.
* Helthchecks for traefik and NOC services.

## Changed

* Less verbose logging.
* Mount service configurations as read-only.
* Store persistent data in named volumes.

## Removed

* `BaseService.compose_etc_dirs` and `.get_compose_etc_dirs()`

## 0.2.0 - 2023-11-23

### Added

* `shell` command.
* Auto-detect docker configuration.
* Auto-select between docker compose plugin and `docker-compose`.
* Config: `expose.open_browser` option.

### Changed

* Configure `docker-compose.yml` logging section when using `json-file` driver.

## 0.1.0 - 2023-11-23

### Added 

* Initial release.
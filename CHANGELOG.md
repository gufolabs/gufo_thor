---
hide:
    - navigation
---
# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

To see unreleased changes, please see the [CHANGELOG on the master branch](https://github.com/gufolabs/gufo_thor/blob/master/CHANGELOG.md) guide.

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
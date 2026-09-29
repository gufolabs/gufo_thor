# AGENTS.md

## Project Overview

Gufo Thor is a command-line tool for deploying and managing [NOC](%5Bhttps://getnoc.com/%5D(https://getnoc.com/)) (ISP network management system) on a single node. Primary audience: new NOC evaluators and developers needing a fast setup environment.

**Stack:** Python 3.10+, Docker + Compose, Ruff, Mypy, Pytest, MkDocs.

## Code Guidelines

-   **Format:** `./scripts/run-dev ruff format src/ tests/`
-   **Lint:** `./scripts/run-dev ruff check src/ tests/`
-   **Type check:** `./scripts/run-dev mypy --strict src/`
-   **Tests:** `./scripts/run-dev pytest -vv`
-   **Run linters, type checks, and tests ONLY through
    `./scripts/run-dev`.** Never run Ruff, Mypy, Pytest, or other
    project development tools directly on the host. This guarantees the
    exact same tool versions as CI.
-   **Build the `dev` stage:** No manual `docker build` or `docker run`
    is required for development tools; use `./scripts/run-dev`.

**Style:** PEP 8 + PEP 561 (type info in dist)

**Language:** All code and text artifacts MUST be in English. This includes code comments, docstrings, logs, help text, user-facing messages, YAML configuration files, examples, and documentation. Never write these in Russian or any other language.

**Docstrings:** Every public class and method must have a docstring following the project's `Attributes / Args / Returns` convention (see existing code for examples).

## Architecture

### Service & Component Loading

Services are **lazy-loaded via Gufo Loader** (entry points). The 50+ modules in `services/` do **not** get imported on startup. When adding a new service/component:

1.  Create `src/gufo/thor/services/<name>.py`
2.  Register via entry point in `pyproject.toml`
3.  It becomes available as `loader[<name>]`

The same loader pattern applies to `targets/` and `labs/`. Currently only `compose` target is implemented; the roadmap includes k8s and Apple Container.

### Config

-   `Config` resides in `src/gufo/thor/config.py`
-   Parses `thor.yml` (YAML)
-   New fields must be: added as typed attrs on the Config model,
    reflected in `get_sample()` templates (`simple`, `common`, `lab1`),
    and documented in `examples/thor.yml`.

### CLI

-   CLI lives in `src/gufo/thor/cli.py`
-   Subcommands are methods `handle_<cmdname>` on the `Cli` class
-   Always return `ExitCode.OK` or `ExitCode.ERR`
-   Uses `argparse` subparsers; new commands require parser setup in `run()`
-   Use `self.config` and `self.target` cached properties to access
    Config and Target instances

### Targets (Docker Backends)

-   `BaseTarget` in `targets/base.py` defines the interface
-   Implementation `ComposeTarget` in `targets/compose.py`
-   `loader["compose"]` instantiates the target in `Cli.target`
-   New backends must implement the `BaseTarget` interface.

### Labs

-   Lab nodes (VyOS, etc.) are for interactive testing/validation.
-   Registered via `labs/base.py` loader.

## Test Standards

-   **Runner:** `./scripts/run-dev pytest -vv`
-   **Coverage target:** 100% wherever possible
-   **Service tests:** Mock Docker and Config --- never spin up real
    containers
-   **Test location:** `tests/`

## Documentation

-   **Serve docs:** `./scripts/run-dev mkdocs serve`
-   **Build & deploy:** `./scripts/run-dev mkdocs gh-deploy --strict --force`
-   **Review:** Use [Grammarly](%5Bhttps://grammarly.com%5D(https://grammarly.com)) for English checks

## Useful Commands

``` bash
# Format
./scripts/run-dev ruff format src/ tests/

# Lint
./scripts/run-dev ruff check src/ tests/

# MyPy (strict)
./scripts/run-dev mypy --strict src/

# Tests
./scripts/run-dev pytest -vv

# Coverage
./scripts/run-dev coverage run -m pytest -vv
./scripts/run-dev coverage report

# Package
./scripts/run-dev python -m build --sdist --wheel

# Docs
./scripts/run-dev mkdocs serve
```

## Known Patterns & Gotchas

### `--migrate` / `--no-migrate` (up command)

These flags are **mutually exclusive**. The code validates this at runtime and logs an error if both are passed.

### Browser Auto-Open

The `up` command opens the browser **only** if `expose.open_browser: true` is set in `thor.yml`. It uses standard OS utilities to launch the browser on all platforms (Linux/WSL/macOS/Windows).

# AGENTS.md

## Project Overview

Gufo Thor is a command-line tool for deploying and managing [NOC](https://getnoc.com/) (ISP network management system) on a single node. Primary audience: new NOC evaluators and developers needing a fast setup environment.

**Stack:** Python 3.9+, Docker + Compose, Ruff, Mypy, Pytest, MkDocs.

## Code Guidelines

- **Format:** `ruff format src/ tests/`
- **Lint:** `ruff check src/ tests/`
- **Run linters ONLY in the dev container.** Never run them on the host — this avoids pulling tool versions into your host environment and guarantees you're using the exact same ruff/mypy versions as CI.

  **Build the `dev` stage:**
  ```bash
  $ docker build --target dev -t gufo_thor_dev .
  ```

  **Run linting:**
  ```bash
  $ docker run --rm -v .:/workspaces/gufo_thor -w /workspaces/gufo_thor gufo_thor_dev ruff check src/ tests/
  $ docker run --rm -v .:/workspaces/gufo_thor -w /workspaces/gufo_thor gufo_thor_dev ruff format --check src/ tests/
  $ docker run --rm -v .:/workspaces/gufo_thor -w /workspaces/gufo_thor gufo_thor_dev mypy --strict src/
  ```
- **Type check:** `mypy --strict src/`
- **Style:** PEP 8 + PEP 561 (type info in dist)
- **Language:** All code and text artifacts MUST be in English. This includes code comments, docstrings, logs, help text, user-facing messages, YAML configuration files, examples, and documentation. Never write these in Russian or any other language.
- **Docstrings:** Every public class and method must have a docstring following the project's `Attributes / Args / Returns` convention (see existing code for examples).

## Architecture

### Service & Component Loading

Services are **lazy-loaded via Gufo Loader** (entry points). The 50+ modules in `services/` do **not** get imported on startup. When adding a new service/component:

1. Create `src/gufo/thor/services/<name>.py`
2. Register via entry point in `pyproject.toml`
3. It becomes available as `loader[<name>]`

The same loader pattern applies to `targets/` and `labs/`. Currently only `compose` target is implemented; the roadmap includes k8s and Apple Container.

### Config

- `Config` resides in `src/gufo/thor/config.py`
- Parses `thor.yml` (YAML)
- New fields must be: added as typed attrs on the Config model, reflected in `get_sample()` templates (`simple`, `common`, `lab1`), and documented in `examples/thor.yml`.

### CLI

- CLI lives in `src/gufo/thor/cli.py`
- Subcommands are methods `handle_<cmdname>` on the `Cli` class
- Always return `ExitCode.OK` or `ExitCode.ERR`
- Uses `argparse` subparsers; new commands require parser setup in `run()`
- Use `self.config` and `self.target` cached properties to access Config and Target instances

### Targets (Docker Backends)

- `BaseTarget` in `targets/base.py` defines the interface
- Implementation `ComposeTarget` in `targets/compose.py`
- `loader["compose"]` instantiates the target in `Cli.target`
- New backends must implement the `BaseTarget` interface.

### Labs

- Lab nodes (VyOS, etc.) are for interactive testing/validation.
- Registered via `labs/base.py` loader.

## Test Standards

- **Runner:** `pytest -vv`
- **Coverage target:** 100% wherever possible
- **Service tests:** Mock Docker and Config — never spin up real containers
- **Test location:** `tests/`

## Documentation

- **Serve docs:** `mkdocs serve`
- **Build & deploy:** `mkdocs gh-deploy --strict --force`
- **Review:** Use [Grammarly](https://grammarly.com) for English checks

## Useful Commands

```bash
# Format
ruff format src/ tests/

# Lint
ruff check src/ tests/

# MyPy (strict)
mypy --strict src/

# Tests
pytest -vv

# Coverage
coverage run -m pytest -vv
coverage report

# Package
python -m build --sdist --wheel

# Docs
mkdocs serve
```

## Known Patterns & Gotchas

### `--migrate` / `--no-migrate` (up command)
These flags are **mutually exclusive**. The code validates this at runtime and logs an error if both are passed.

### Browser Auto-Open
The `up` command opens the browser **only** if `expose.open_browser: true` is set in `thor.yml`. It uses standard OS utilities to launch the browser on all platforms (Linux/WSL/macOS/Windows).

### Versioning
Current version: `0.13.0` (in `src/gufo/thor/__init__.py`). Update in `__init__.py` and `pyproject.toml` on release.

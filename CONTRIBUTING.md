# Contributing to Gufo Thor

Thank you for your interest in contributing! Before submitting a patch or issue, please review the following guidelines.

## FAQ

Please check the [FAQ](docs/faq.md) for answers to common questions about contributing, setup, and usage.

## Code of Conduct

This project follows the
[Gufo Stack Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful and constructive in all interactions.

## Reporting Issues and Discussions

- Report bugs and feature requests via [Issues](https://github.com/gufolabs/gufo_thor/issues).
- Discuss ideas and ask questions in [Discussions](https://github.com/gufolabs/gufo_thor/discussions/).
- Code contributions go via [Pull Requests](#pull-requests).

## Pull Requests

Before opening a PR, make sure you're familiar with the project conventions:

- **[Project Structure](docs/dev/codebase.md)** — directory layout and key files
- **[Code Quality Standards](docs/dev/codequality.md)** — formatting (ruff), linting, mypy strict, test coverage expectations
- **[Development Environment](docs/dev/environment.md)** — VS Code dev container for a ready-to-go setup
- **[Building and Testing](docs/dev/testing.md)** — how to build, run tests, and check linting locally
- **[Supported Standards](docs/dev/standards.md)** — PEP, RFC, and other relevant standards and regulations

### PR Checklist

- [ ] Code follows [code quality standards](docs/dev/codequality.md)
- [ ] Tests pass (`pytest -vv`) and lints are clean (`ruff`, `mypy --strict`)
- [ ] Your changes follow the existing conventions (see [codebase overview](docs/dev/codebase.md))
- [ ] If applicable, documentation is updated to match your changes
- [ ] CHANGELOG.md updated with a brief description of your change

### PR Guidelines

- One change per PR. Keep diffs focused.
- Link any relevant issues in the PR description.
- Use a clear commit message (imperative mood, e.g., "add validation for X").
- If your PR touches the configuration schema, make sure the config docs reflect the changes.

## Where to Start

New to the project? Check the [developer guide](docs/dev/index.md) for an overview of the codebase, tooling, and workflows.

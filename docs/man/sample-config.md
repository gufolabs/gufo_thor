# gufo-thor sample-config

Write a sample configuration to `thor.yml` in the current directory.

## Synopsis

```shell
gufo-thor sample-config [-t TEMPLATE]
```

## Options

* `-t`, `--template TEMPLATE`: Select a sample configuration template. Defaults to `simple`.

Available templates:

* `simple`: Web-only setup.
* `common`: Web interface, hardware integration, and event-processing pipeline.
* `lab1`: Full hardware integration stack and a sample lab with three VyOS routers connected in a ring.

The command exits with an error if `thor.yml` already exists. See [Configuration Templates](../reference/templates.md) for available templates.

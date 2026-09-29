# gufo-thor up

Prepare and launch NOC.

## Synopsis

```shell
gufo-thor up [--migrate | --no-migrate]
```

## Options

* `--migrate`: Run database migrations.
* `--no-migrate`: Skip database migrations.

The migration options cannot be used together. The command prints the web interface URL and opens a browser only when `expose.open_browser` is enabled in `thor.yml`.

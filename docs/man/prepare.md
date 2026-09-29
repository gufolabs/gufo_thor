# gufo-thor prepare

Generate the service configuration required to run NOC. This command only prepares configuration files; it does not start containers.

## Synopsis

```shell
gufo-thor prepare
```

`gufo-thor up` runs this preparation automatically before starting NOC. If `thor.yml` does not exist, `prepare` writes the default sample configuration before generating service configuration.

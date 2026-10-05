# NOC Section

Defines common noc configuration.

## version { #version }

Selects the NOC release and the matching Docker images for NOC and its infrastructure services. The default and currently supported value is `26-dev`.

``` yaml
noc:
    version: "26-dev"
```

## tag { #tag }

Optional Docker image tag override for NOC application services. Normally, leave this unset and select the release with `version`; use `tag` mainly for development. When set, it replaces the tag in the NOC image selected by `version`. A service-specific tag takes precedence over this setting.

``` yaml
noc:
    version: "26-dev"
    tag: "my-feature-branch"
```

## path { #path }

NOC source code path to override container's `/opt/noc`.
Used for development and allows to expose local changes
directly in container.

``` yaml
noc:
    path: /home/joe/work/noc
```

## custom { custom }

NOC custom code path. Allows to mount NOC customizations
from local host.

``` yaml
noc:
    custom: /home/joe/work/noc-custom
```

## installation_name { #installation_name }

Installation name as shown in web interface. Has default
value `Unconfigured Installation`.

``` yaml
noc:
    installation_name: "ACME INC"
```

## migrate { #migrate }

Run migrations on start. Has default value `True`.

``` yaml
noc:
    migrate: true
```

## theme { #theme }

Web interface theme, one of: `noc`, `gray`. Has default value `noc`.

``` yaml
noc:
    theme: noc
```

## language { #language }

Web interface language, one of: `en`, `ru`.

``` yaml
noc:
    language: en
```

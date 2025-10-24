# NOC Section

Defines common noc configuration.

## tag { #tag }

Defines docker image tag. Default value is `master`.

``` yaml
noc:
    tag: "24.1"
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
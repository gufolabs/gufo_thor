# thor.yml Configuration Reference

This topic describes `thor.yml` file format version `1.0`.

`thor.yml` is [YAML][YAML] file defining [version](#version) and [project](#project) keys and
[noc](#noc-section), [expose](#expose-section), and [services](#services-section) sections.

## version

File format version. Must have value `1.0`.

``` yaml
version: "1.0"
```

## project

Project name. Defines docker containers name prefix. Used
to distingush container names when multiple thor projects
are used on same host. By default, the name of directory
in which the `thor.yml` file locates is used as project name.

``` yaml
project: mynoc
```

## NOC Section { #noc }

Defines common noc configuration.

### tag { #noc-tag }

Defines docker image tag. Default value is `master`.

``` yaml
noc:
    tag: "24.1"
```

### path { #noc-path }

NOC source code path to override container's `/opt/noc`.
Used for development and allows to expose local changes
directly in container.

``` yaml
noc:
    path: /home/joe/work/noc
```

### custom { #noc-custom }

NOC custom code path. Allows to mount NOC customizations
from local host.

``` yaml
noc:
    custom: /home/joe/work/noc-custom
```

### installation_name { #noc-installation-name }

Installation name as shown in web interface. Has default
value `Unconfigured Installation`.

``` yaml
noc:
    installation_name: "ACME INC"
```

### migrate { #noc-migrate }

Run migrations on start. Has default value `True`.

``` yaml
noc:
    migrate: true
```

## Expose Section { #expose }

Web interface entrypoint configuration.

### domain_name { #expose-domain-name }

Domain name for web interface. By default has the value `go.getnoc.com`
which techninally resolves to the localhost. When using default domain
name the Gufo Thor is able to sign the domain certificate in fully
transparent manner.

!!! warning

    If you wish to change the `domain_name` you have to
    generate private key and sign the certificate by yourself.

``` yaml
expose:
    domain_name: go.getnoc.com
```

### port { #expose-port }

Web interface port. `32777` is used by default.

```
expose:
    port: 32777
```

### open_browser { #expose-open-browser }

If set to `true`, open `https://<domain_name>:<port>/` in browser
on every `gufo-thor up`

```
expose:
    open_browser: true
```

## Services Section { #services }

This section contains a list of services to start. Services can be specified as

* list of service names.
  ``` yaml
  services: [web, card]
  ```
* mapping of service configuration items.
  ``` yaml
  services:
    web:
      scale: 4
    card:
      scale: 2
  ```

### tag { #services-tag }

Docker image tag to override global [tag](#noc-tag) section for given service.

``` yaml
services:
    web:
        tag: "stable"
```


### scale { #services-scale }

Number of instances of service to launch. Note, not all services
are scalable, so refer to the [NOC Services Reference][Services Reference].

``` yaml
services:
    web:
        scale: 4
```

[YAML]: https://yaml.org/
[Services Reference]: https://getnoc.com/services-reference/
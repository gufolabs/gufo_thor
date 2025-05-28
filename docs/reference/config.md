# thor.yml Configuration Reference

This topic describes `thor.yml` file format version `1.0`.

`thor.yml` is [YAML][YAML] file defining:

* [version](#version)
* [project](#project)
* [noc](#noc)
* [expose](#expose)
* [pools](#pools)
* [services](#services)
* [labs](#labs)

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

### web { #expose-web }

Web interface address and port.

```
expose:
    web:
        address: 127.0.0.1
        port: 32777
```

### open_browser { #expose-open-browser }

If set to `true`, open `https://<domain_name>:<port>/` in browser
on every `gufo-thor up`

```
expose:
    open_browser: true
```

## Pools Section { #pools }

This section contains a pools definitions. Key is pool name.

``` yaml
pools:
  subnet: 10.0.2.0/24
```

### subnet { #pools-subnet }

Subnet allocated to pool connection network. [pool-gw](#labs-nodes-pool-gw) and
pool services' addresses will be allocated from this subnet.

``` yaml
pools:
  subnet: 10.0.2.0/24
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

## Labs Section {#labs}

Defines network labs. Each lab contains network nodes and links.

Example:

```yaml
labs:
  lab1:
    pool: test
    nodes:
      r1:
        type: vyos
        version: 1.4
        router-id: 10.0.0.1
      r2:
        type: vyos
        version: 1.4
        router-id: 10.0.0.2
    links:
      - prefix: 10.0.1.0/30
        node-a: r1
        node-b: r2
        protocols:
          isis:
            metric: 1000
```

`lab1` is the lab name. A configuration file can define multiple labs.

### pool {#labs-pool }

If lab is attached to dedicated pool, `pool` must refer to one of [pools](#pools).
If pool is set, one of the nodes must be designated as [pool-gw](#labs-nodes-pool-gw)

```yaml
labs:
  lab1:
    pool: test
```


### nodes {#labs-nodes}

Defines the list of nodes in the lab. Node names are used as keys.

```yaml
labs:
  lab1:
    nodes:
      r1:
        type: vyos
        version: 1.4
        router-id: 10.0.0.1
      r2:
        type: vyos
        version: 1.4
        router-id: 10.0.0.2
```

#### type {#labs-nodes-type}

Specifies the node type. Supported values:

- `vyos` — VyOS virtual router.

Example:

```yaml
labs:
  lab1:
    nodes:
      r1:
        type: vyos
```

#### version {#labs-nodes-version}

Image version for the node.

| Type | Version |
| ---- | ------- |
| vyos | 1.4     |

Example:

```yaml
labs:
  lab1:
    nodes:
      r1:
        type: vyos
        version: "1.4"
```

#### router-id {#labs-nodes-router-id}

Specifies the router ID, assigned to the loopback interface.

```yaml
labs:
  lab1:
    nodes:
      r1:
        router-id: 10.0.0.1
```

#### pool-gw {#labs-nodes-pool-gw}

Node will serve as designated gateway to pools. Only one node of lab may be marked as `pool-gw`.

```yaml
labs:
  lab1:
    nodes:
      r1:
        pool-gw: true
```


### links {#labs-links}

Defines the connections between nodes. Each link is described as an item in the list.

```yaml
labs:
  lab1:
    links:
      - prefix: 10.0.1.0/30
        node-a: r1
        node-b: r2
        protocols:
          isis:
            metric: 1000
```

#### prefix {#labs-links-prefix}

Network prefix used for the link, typically a `/30` subnet.

```yaml
labs:
  lab1:
    links:
      - prefix: 10.0.1.0/30
```

#### node-a {#labs-links-node-a}

Starting node of the link.

```yaml
labs:
  lab1:
    links:
      - node-a: r1
```

#### node-b {#labs-links-node-b}

Ending node of the link.

```yaml
labs:
  lab1:
    links:
      - node-b: r2
```

#### protocols {#labs-links-protocols}

Defines enabled protocols on the link.

```yaml
labs:
  lab1:
    links:
      - protocols:
          isis:
            metric: 1000
```

##### isis {#labs-links-protocols-isis}

Enables the IS-IS protocol on the link.

```yaml
labs:
  lab1:
    links:
      - prefix: 10.0.1.0/30
        node-a: r1
        node-b: r2
        protocols:
          isis:
            metric: 1000
```

###### metric {#labs-links-protocols-isis-metric}

Optional IS-IS metric for the link.

```yaml
labs:
  lab1:
    links:
      - protocols:
          isis:
            metric: 1000
```

[YAML]: https://yaml.org/
[Services Reference]: https://getnoc.com/services-reference/
# Labs Section

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

## pool {#pool }

If lab is attached to dedicated pool, `pool` must refer to one of [pools](pools.md).
If pool is set, one of the nodes must be designated as [pool-gw](#nodes-pool-gw)

```yaml
labs:
  lab1:
    pool: test
```


## nodes {#nodes}

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

### type {#nodes-type}

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

### version {#nodes-version}

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

### router-id {#nodes-router-id}

Specifies the router ID, assigned to the loopback interface.

```yaml
labs:
  lab1:
    nodes:
      r1:
        router-id: 10.0.0.1
```

### pool-gw {#nodes-pool-gw}

Node will serve as designated gateway to pools. Only one node of lab may be marked as `pool-gw`.

```yaml
labs:
  lab1:
    nodes:
      r1:
        pool-gw: true
```

### users { #nodes-users }
List of user credentials

``` yaml
labs:
  lab1:
    nodes:
      r1:
        users:
          - user: user1
            password: secret1
```

#### user { #nodes-users-user }
User name.

``` yaml
labs:
  lab1:
    nodes:
      r1:
        users:
          - user: user1
```

#### password { #nodes-users-password }
Plaintext password.

``` yaml
labs:
  lab1:
    nodes:
      r1:
        users:
          - password: secret1
```

### snmp { #nodes-snmp }
Set up snmp credentials. Contains a list of items.

``` yaml
labs:
  lab1:
    nodes:
      r1:
        snmp:
          - version: v2c
            community: public
```

#### version { #nodes-snmp-version }

SNMP protocol version. Following versions are supported:

- `v2c`

#### community { #nodes-snmp-comminity }

SNMP community for SNMP v2c. Requred, when version is set to `v2c`.

## links {#links}

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

## prefix {#links-prefix}

Network prefix used for the link, typically a `/30` subnet.

```yaml
labs:
  lab1:
    links:
      - prefix: 10.0.1.0/30
```

## node-a {#links-node-a}

Starting node of the link.

```yaml
labs:
  lab1:
    links:
      - node-a: r1
```

## node-b {#links-node-b}

Ending node of the link.

```yaml
labs:
  lab1:
    links:
      - node-b: r2
```

## protocols {#links-protocols}

Defines enabled protocols on the link.

```yaml
labs:
  lab1:
    links:
      - protocols:
          isis:
            metric: 1000
```

### isis {#links-protocols-isis}

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

### metric {#links-protocols-isis-metric}

Optional IS-IS metric for the link.

```yaml
labs:
  lab1:
    links:
      - protocols:
          isis:
            metric: 1000
```
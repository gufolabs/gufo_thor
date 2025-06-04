# Pools Section

This section contains a pools definitions. Key is pool name.

``` yaml
pools:
  mypool:
    subnet: 10.0.2.0/24
```

## subnet { #subnet }

Subnet allocated to pool connection network. [pool-gw](labs.md#nodes-pool-gw) and
pool services' addresses will be allocated from this subnet.

``` yaml
pools:
  mypool:
    subnet: 10.0.2.0/24
```

## address { #address }

Address section allow to pin particolar addresses to services in the pool.

``` yaml
pools:
  mypool:
    address:
      gw: 10.0.2.1
      syslog: 10.0.2.2
      trap: 10.0.2.3
```

### gw { #address-gw }
Set default gateway to the pools' network. Uses first free IP address in [subnet](#subnet)
if not set.

``` yaml
pools:
  mypool:
    address:
      gw: 10.0.2.1
```

### syslog { #address-syslog }
Set up address for syslog collector in the pool. Will be bound to `syslogcollector` service.

``` yaml
pools:
  mypool:
    address:
      syslog: 10.0.2.2
```

### trap { #address-trap }
Set up address for syslog collector in the pool. Will be bound to `trapcollector` service.

``` yaml
pools:
  mypool:
    address:
      trap: 10.0.2.3
```
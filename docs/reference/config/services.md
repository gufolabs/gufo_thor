# Services Section

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

## tag { #tag }

Docker image tag to override global [tag](noc.md#tag) section for given service.

``` yaml
services:
    web:
        tag: "stable"
```


## scale { #scale }

Number of instances of service to launch. Note, not all services
are scalable, so refer to the [NOC Services Reference][Services Reference].

``` yaml
services:
    web:
        scale: 4
```

[Services Reference]: https://getnoc.com/services-reference/

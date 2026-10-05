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

For NOC application services, optionally override the image tag selected by [NOC version](noc.md#version) and global [NOC tag](noc.md#tag). Use this setting mainly for development; it takes precedence over `noc.tag`.

``` yaml
services:
    web:
        tag: "my-feature-branch"
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

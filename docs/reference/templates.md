# Gufo Thor Configuration Templates

Gufo Thor is provided with several predefined templates
which addresses various patterns of usage:

* [simple](#simple) - web-only setup.
* [common](#common) - web and hardware integration.
* [lab1](#lab1) - Full hardware integration stack and lab with 3 VyOS routers.

To generate template config use:

``` shell
gufo-thor sample-config -t <template name>
```

## simple

Simple web-only installation.

``` yaml
--8<-- "src/gufo/thor/samples/simple.yml"
```

## common

Installation with web interface, hardware integration,
and event-processing pipeline.

``` yaml
--8<-- "src/gufo/thor/samples/common.yml"
```

## lab1

Full hardware-integration stack with sample lab with
3 VyOS routers connected in ring.

``` yaml
--8<-- "src/gufo/thor/samples/lab1.yml"
```

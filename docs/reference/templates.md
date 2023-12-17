# Gufo Thor Configuration Templates

Gufo Thor is provided with several predefined templates
which addresses various patterns of usage:

* [simple](#simple) - web-only setup.
* [common](#common) - web and hardware integration.

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

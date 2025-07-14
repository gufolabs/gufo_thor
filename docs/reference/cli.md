# Command Line Reference

Gufo Thor is managed via `gufo-thor` command.

## Show Version

To show Gufo Thor version use:
```
gufo-thor version
```

## Generate Sample Config

To generate sample config use:

```
gufo-thor sample-config -t <config_name>
```

where `<config_name>` is the name of the template.
Refer to the [Configuration Templates](templates.md) for details.

## Prepare

To generate all necessary configs without launching NOC use

```
gufo-thor prepare
```

## Running NOC

To run NOC use:

```
gufo-thor up
```

!!! note

    This command performs [prepare](#prepare) automatically.

## Stopping NOC

To stop NOC use:

```
gufo-thor stop
```

## Running Shell

To run NOC shell use:

```
gufo-thor shell
```

## Show Stats

To show NOC processes' statistics use:

```
gufo-thor stats
```

## Destroying Installation

To destroy installation and free resources:

```
gufo-thor destroy
```
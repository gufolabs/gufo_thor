# Command Line Reference

Gufo Thor is managed via `gufo-thor` command.

## Show Version

To show Gufo Thor version use:
```
gufo-thor version
```

## Backups

Create a backup of PostgreSQL, MongoDB, and ClickHouse:

```shell
gufo-thor backup create
```

Pass an optional first argument to choose the backup directory name. Without it, Thor uses the current timestamp. Specify one or more of `--postgres`, `--mongo`, and `--clickhouse` to back up selected services. If none are specified, all supported services are backed up:

```shell
gufo-thor backup create before-upgrade
gufo-thor backup create --postgres
gufo-thor backup create --mongo --clickhouse
```

List backups in newest-first order, with their duration and per-database and
total sizes:

```shell
gufo-thor backup ls
```

## Generate Sample Config

To generate sample config use:

```
gufo-thor sample-config -t <config_name>
```

where `<config_name>` is the name of the template. Refer to the [Configuration Templates](templates.md) for details.

Available templates:

* `simple`: Web-only setup.
* `common`: Web interface, hardware integration, and event-processing pipeline.
* `lab1`: Full hardware integration stack and a sample lab with three VyOS routers connected in a ring.

## Prepare

To generate all necessary configs without launching NOC use

```
gufo-thor prepare
```

This command only prepares configuration files; it does not start containers. The `up` command performs this preparation automatically.

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

## Restarting Process

To restart NOC process use:

```
gufo-thor restart <process name>
```

**Example:**

```
gufo-thor restart web
```

## Running Shell

To run NOC shell use:

```
gufo-thor shell
```

Thor starts a separate temporary container with the NOC image, connected to the configured databases, and opens Bash so you can run NOC commands.

## Show Stats

To show NOC processes' statistics use:

```
gufo-thor stats
```

Example output:

```text
CONTAINER ID   NAME                 CPU %   MEM USAGE / LIMIT   MEM %   NET I/O        BLOCK I/O   PIDS
71d5c1a4b980   thor-web-1            0.12%   312MiB / 15.6GiB   1.95%   2.1MB / 1MB   0B / 0B     28
8ea23ff177c3   thor-postgres-1       0.04%   96MiB / 15.6GiB    0.60%   840kB / 1MB   0B / 0B     12
```

The command streams live statistics; names and values depend on the installation.

## Show Process' Logs

To show NOC process' logs use:

```
gufo-thor logs <process name>
```

**Example:**

```
gufo-thor logs web
```

To use logs in follow mode:

```
gufo-thor logs -f <process name>
```

## Upgrading NOC

To upgrade NOC to a new version use:

```
gufo-thor upgrade
```

The command pulls all images in the Compose project, including NOC services, databases, and other infrastructure components.

## Destroying Installation

To destroy installation and free resources:

```
gufo-thor destroy
```

## Pausing/unpausing Container

To temporary pause NOC services' containers use:

```
gufo-thor pause
```

Paused containers remain running, preserve existing connections, and receive no CPU time until resumed.

To resume execution:

```
gufo-thor unpause
```

This resumes the containers and their processes; their existing connections are preserved during the pause.

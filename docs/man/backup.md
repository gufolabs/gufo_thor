# gufo-thor backup

Create and list database backups. Backups include PostgreSQL, MongoDB, and
ClickHouse by default. Use `--postgres`, `--mongo`, and `--clickhouse` to
select one or more services; when no service options are specified, all
supported database services are backed up.

## Synopsis

```shell
gufo-thor backup create [--name NAME] [--postgres] [--mongo] [--clickhouse]
gufo-thor backup ls
```

## Commands

### create

Create backups for supported database services. If `--name` is omitted, Thor
uses the current timestamp. Backup files and generated restore scripts are
stored in `data/backup/<name>`.

Names must start with a letter or digit and may contain letters, digits,
periods, underscores, and hyphens; the maximum length is 128 characters.

```shell
gufo-thor backup create
gufo-thor backup create --name before-upgrade
gufo-thor backup create --name postgres-only --postgres
gufo-thor backup create --name databases --postgres --mongo
gufo-thor backup create --clickhouse
```

### ls

List backups sorted by creation timestamp, newest first. The table reports the
duration and size of each database dump, along with the total size.

```shell
gufo-thor backup ls
```

```text
name           | timestamp           | duration | postgres size | mongo size | clickhouse size | total size
---------------+---------------------+----------+---------------+------------+-----------------+-----------
before-upgrade | 2026-10-01 15:59:33 | 42s      |         720.4K |       8.2M |             4.1M |     13.0M
```

# gufo-thor restore

Restore database dumps from a local backup. Without service options, Thor restores every supported dump found in the backup directory. Use `--postgres`, `--mongo`, and `--clickhouse` to select one or more services.

## Synopsis

```shell
gufo-thor restore <name> [--postgres] [--mongo] [--clickhouse]
```

The backup must exist in `data/backup/<name>`. Thor starts any selected database containers that are stopped and pauses running application containers during the restore. Containers that Thor started are stopped afterward, and paused application containers are resumed.

If service options are omitted, all dump files present in the backup are restored. If options are specified, every selected service must have a dump in the backup.

```shell
gufo-thor restore before-upgrade
gufo-thor restore before-upgrade --postgres
gufo-thor restore before-upgrade --postgres --mongo
```

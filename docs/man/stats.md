# gufo-thor stats

Show container statistics.

## Synopsis

```shell
gufo-thor stats
```

The command displays the live resource usage reported by Docker Compose. Example:

```text
CONTAINER ID   NAME                 CPU %   MEM USAGE / LIMIT   MEM %   NET I/O        BLOCK I/O   PIDS
71d5c1a4b980   thor-web-1            0.12%   312MiB / 15.6GiB   1.95%   2.1MB / 1MB   0B / 0B     28
8ea23ff177c3   thor-postgres-1       0.04%   96MiB / 15.6GiB    0.60%   840kB / 1MB   0B / 0B     12
```

Container names and values vary by installation and change while the command is running.

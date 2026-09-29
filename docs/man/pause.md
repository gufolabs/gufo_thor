# gufo-thor pause

Pause NOC service containers.

## Synopsis

```shell
gufo-thor pause
```

Paused containers remain running, and their existing connections are preserved. Their processes receive no CPU time until the containers are resumed with [`gufo-thor unpause`](unpause.md).

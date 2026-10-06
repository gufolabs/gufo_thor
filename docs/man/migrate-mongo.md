# gufo-thor migrate-mongo

Migrate the MongoDB Feature Compatibility Version (FCV) to the version required by the configured NOC release. MongoDB is upgraded one supported FCV at a time, using the matching MongoDB image for each step.

## Synopsis

```shell
gufo-thor migrate-mongo
```

The command reads the current FCV from the Thor state file. If no FCV is recorded, it assumes the legacy FCV `4.4`. It then migrates through each supported FCV up to the target configured for the selected NOC version, saving the completed FCV after each step.

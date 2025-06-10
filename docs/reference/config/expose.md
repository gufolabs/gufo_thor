# Expose Section

Web interface entrypoint configuration.

## domain_name { #domain-name }

Domain name for web interface. By default has the value `go.getnoc.com`
which techninally resolves to the localhost. When using default domain
name the Gufo Thor is able to sign the domain certificate in fully
transparent manner.

!!! warning

    If you wish to change the `domain_name` you have to
    generate private key and sign the certificate by yourself.

``` yaml
expose:
    domain_name: go.getnoc.com
```

## web { #web }

Web interface address and port.

```
expose:
    web:
        address: 127.0.0.1
        port: 32777
```

## mongo { #mongo }
Expose mongo to host:

```
expose:
    mongo: 27017
```

## postgres { #postgres }
Expose postgres to host:

```
expose:
    postgres: 5432
```

## open_browser { #open_browser }

If set to `true`, open `https://<domain_name>:<port>/` in browser
on every `gufo-thor up`

```
expose:
    open_browser: true
```
# Gufo Thor

*A simple [NOC][NOC] management and deployment tool.*

[![PyPi version](https://img.shields.io/pypi/v/gufo_thor.svg)](https://pypi.python.org/pypi/gufo_thor/)
![Python Versions](https://img.shields.io/pypi/pyversions/gufo_thor)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Build](https://img.shields.io/github/actions/workflow/status/gufolabs/gufo_thor/py-tests.yml?branch=master)
![Sponsors](https://img.shields.io/github/sponsors/gufolabs)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)

---

**Documentation**: [https://docs.gufolabs.com/gufo_thor/](https://docs.gufolabs.com/gufo_thor/)

**Source Code**: [https://github.com/gufolabs/gufo_thor/](https://github.com/gufolabs/gufo_thor/)

---
Gufo Thor is a simple tool designed for quickly setting up and evaluating [NOC][NOC].
It's tailored for new NOC users who want to assess NOC's capabilities and NOC developers 
who need a fast development environment. Thor takes care of the complexity of NOC management, 
making the process straightforward.

## Prerequisites

To use Thor, make sure you have the following software packages installed:

- Docker
- docker-compose or the compose plugin
- Python 3.8+

## Installation

To install or update Thor, follow these steps:

1. Create a dedicated directory where all configuration files will be stored.
2. Navigate to the newly created directory.
3. Run the installer:
  ```
  curl https://sh.gufolabs.com/thor | sh
  ```
4. After installation, NOC will be launched,
   and your browser will open at  https://go.getnoc.com:32777/
5. Log in as user `admin` with password `admin`.

## NOC Operations Cheat List

Execute all actions from the directory containing the Thor configuration. 
If you are using venv mode, ensure to activate the virtual environment (venv) before utilizing Thor.

``` shell
. ./bin/activate
```

### Start NOC
Use the following command to start NOC:

```
gufo-thor up
```

Once NOC is ready, you will be redirected to https://go.getnoc.com:32777/
Log in using the following credentials:

- **Username:** admin
- **Password:** admin

### Stop NOC

To stop NOC, use the command:

```
gufo-thor stop
```

## Configuration

Thor's configuration is in the thor.yml file. You can use preconfigured defaults:

```
gufo-thor sample-config -t <name>
```

Where `<name>` can be:

* `simple` - Minimal setup with a web interface only.
* `common` - Setup with widely-used features for monitoring and network management.

The thor.yml structure:
```
# Gufo Thor configuration
version: "1.0"
noc:
  tag: master
  installation_name: Unconfigured Installation
expose:
  domain_name: go.getnoc.com
  port: 32777
services: [web, card]
```

Adapt the file to your needs and start NOC:

```
gufo-thor up
```

## On Gufo Stack

This product is a part of [Gufo Stack][Gufo Stack] - the collaborative effort 
led by [Gufo Labs][Gufo Labs]. Our goal is to create a robust and flexible 
set of tools to create network management software and automate 
routine administration tasks.

To do this, we extract the key technologies that have proven themselves 
in the [NOC][NOC] and bring them as separate packages. Then we work on API,
performance tuning, documentation, and testing. The [NOC][NOC] uses the final result
as the external dependencies.

[Gufo Stack][Gufo Stack] makes the [NOC][NOC] better, and this is our primary task. But other products
can benefit from [Gufo Stack][Gufo Stack] too. So we believe that our effort will make 
the other network management products better.

[Gufo Labs]: https://gufolabs.com/
[Gufo Stack]: https://gufolabs.com/products/gufo-stack/
[NOC]: https://getnoc.com/

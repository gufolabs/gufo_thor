---
hide:
    - navigation
---
## Prerequisites

To use Thor, make sure you have the following software packages installed:

- Docker
- docker-compose or the compose plugin
- Python 3.8+

## System-Level Installation

For dedicated NOC hosts, use this installation method. 
It installs Thor and all required libraries into the system default location.

```
curl https://sh.gufolabs.com/thor | sh
```

## Python VENV Installation

For evaluation, testing, and development purposes, use this installation method. 
It creates a dedicated Python virtual environment (venv) and isolates Thor along 
with all dependent libraries from other systems.

```
python -m venv .
. ./bin/activate
curl https://sh.gufolabs.com/thor | sh
```

Later, when using Thor, make sure to activate the virtual environment (venv):

```
. ./bin/activate
```

## Checking the Installation

To check the installation just import the module

```
gufo-thor version
```

## Upgrading

To upgrade existing Gufo Thor installation use pip

```
$ pip3 install --upgrade gufo-thor
```

## Uninstalling

To uninstall Gufo Thor use pip

```
$ pip3 uninstall gufo-thor
```

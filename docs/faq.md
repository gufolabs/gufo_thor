---
hide:
    - navigation
---
# FAQ

## Getting Started with Thor

### Why Thor if Tower exists?

Tower is a comprehensive tool for cluster management. Thor is designed for simple installations: a single NOC node (co-located with or separate from the database nodes).

### How to install Thor?

Install Thor via 

```
curl https://sh.gufolabs.com/thor | sh
```

Complete setup instructions are available in our [Installation guide](installation.md).

### How to upgrade Thor?

Upgrade Thor by running 

```
pip3 install --upgrade gufo-thor
```

Your existing configuration files are preserved automatically. See [Installation guide](installation.md#upgrading)
for details.

### How quickly can I deploy NOC with Thor?
    
Typically, a new NOC installation comes up in 1-2 minutes.

### Is Thor production-ready?
    
Currently, Thor only supports the master branch. Official support for Thor will begin with the NOC 26 release.

## Requirements and Labs

### Does Thor work on macOS?
    
Yes. We provide all Docker images and packages for ARM64, and they work perfectly on macOS.

### What is the best Docker runtime for NOC on macOS?
    
Currently, OrbStack provides the best performance.

### Does Thor work on Windows?

It is not officially supported. While it can run through Windows Subsystem for Linux (WSL2), we do not recommend this configuration at the moment.

### How much RAM do I need to try NOC?

About 4GB for NOC itself, plus around 1GB for each virtual router in the lab.

### Can I try NOC without network hardware?
    
Yes, the *Labs* feature allows you to spin up a network lab in containers and connect it to NOC.

### Can I use Thor for NOC development?
    
Yes. The main development of NOC is currently done using Thor.

## Architecture and Design

### Is Thor a Docker version of NOC?

No. Thor is an orchestration tool, not a NOC distribution. It currently uses docker-compose as a backend, but the plan is to also support Apple Container and Kubernetes in the future.

### What is the main difference between Thor and Tower?

Tower provides a UI, a cluster configuration database, and Ansible-based deployment. Thor translates a text-based YAML configuration file into directives for the target backend.

### Why not Helm?

Helm is Kubernetes-specific and adds unnecessary complexity for single-node or small installations. Thor, on the other hand, has built-in knowledge of NOC services and their dependencies, which minimizes configuration errors and accelerates the initial experience. Docker-compose fits the majority of use cases better in these scenarios. Support for Kubernetes backends will be added in future releases.

### Why not just docker-compose.yml?
    
NOC is highly flexible, with complex inter-service dependencies. Thor guarantees a fully functional deployment environment. Furthermore, Thor generates configuration files compliant with the strictest security standards and best practices.

### Will I lose data on update?

No. NOC stores all its data in persistent Docker volumes. Thor only manages the service containers.

### Can I use my own Docker images?

Yes, you can override any image in the thor.yml configuration file under the services section.

## Support and License

### What is the license of Thor?

Thor is released under the [3-clause BSD License](LICENSE.md).
    
### Where can I get support?

Please use GitHub Issues for bugs or Discussions for feature requests.

### Can I help the NOC project financially?

Yes, you can support our work via [GitHub Sponsors](https://github.com/sponsors/gufolabs) or [Buy Me a Coffee](https://www.buymeacoffee.com/dvolodin). Your contributions help us continue developing and maintaining NOC as a high-quality open-source project.

## About Gufo

### What does "Gufo" mean?

*Gufo* means *the Owl* in Italian.

### Why the owls?

We love owls and the viable parts of our technologies were proven at the project, named "the Owl".

### What is "Gufo Labs"?

[Gufo Labs](https://gufolabs.com/) is the italian company specialized in network and IT consulting, and on software research.

### What is "Gufo Stack"?

We've extracted core components behind the [NOC](https://getnoc.com/) and released them as independent packages, available under the terms of the 3-clause BSD license. Our software shares common code quality standards and is battle-proven under the high load. We hope our key components will help the engineers and the developers to build reliable networks and robust network management software. See [more for details](https://gufolabs.com/products/gufo-stack/).

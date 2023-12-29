# ---------------------------------------------------------------------
# Gufo Thor: BaseService
# ---------------------------------------------------------------------
# Copyright (C) 2023, Gufo Labs
# ---------------------------------------------------------------------
"""
BaseService definition.

Attributes:
    loader: The service loader.
"""

# Python Modules
import operator
from abc import ABC
from enum import Enum
from importlib import resources
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type, Union

import jinja2

# Third-party modules
from gufo.loader import Loader

# Gufo Thor modules
from ..config import Config, ServiceConfig
from ..docker import docker
from ..utils import write_file


class ComposeDependsCondition(Enum):
    """
    depends_on condition.

    Attributes:
        STARTED: Run dependends after the service is started.
        HEALTHY: Run dependends after the service is started
            and entered the healhy state.
        COMPLETED_SUCCESSFULLY: Run dependends after the service
            is started and terminated successfully.
    """

    STARTED = "service_started"
    HEALTHY = "service_healthy"
    COMPLETED_SUCCESSFULLY = "service_completed_successfully"


class BaseService(ABC):
    """
    Base class for the service declaration.

    Attributes:
        name: Service name
        is_noc: True, if the service is belongs to NOC
        dependencies: Optional list of dependencies
        compose_image: docker image name. Override `get_compose_image`
            to implement config-depended behavior.
        compose_depends_condition: Condition for all dependend
            services. Override `get_compose_dependens_condition`
            to implement custom behavior.
        compose_healthcheck: Healtcheck section, if any.
            Override `get_compose_healthcheck`
            to implement custom behavior.
        compose_command: `command` section, if any.
            Override `get_compose_command` to implement
            custom behavior.
        compose_entrypoint: `entrypoint` section, if any.
            Override `get_compose_entrypoint`
            to implement custom behavior.
        compose_working_dir: `working_dir` section if any.
            Override `get_compose_working_dir`
            to implement custom behavior.
        compose_volumes: `volumes` section, if any.
            Override `get_compose_volumes`
            to implement custom behavior.
        compose_volumes_config: Global `volumes` section, if any.
            Override `get_compose_volumes_config`
            to implement custom behavior.
        compose_environment: `environment` section, if any.
            Override `get_compose_environment`
            to implement custom behavior.
        compose_extra: Additional parameters to be merged
            with the compose config.
            Override `get_compose_extra`
            to implement custom behavior.
        service_discovery: Optional name -> port mappings.
            Override `get_service_discovery` to implement
            custom behavior.
        allow_scale: If the service allows running multiple
            instances.
        require_slots: If the service requires slots creation.
        expose_http_prefix: Optional prefix to be exposed on edge proxy.
            Override `get_exposed_http_prefix` to implement
            custom behavior.
        require_http_auth: True, if the service protected by
            http auth proxy.
        rewrite_http_prefix: If set, rewrite matched http prefix
            before passing request to upstream.
    """

    name: str
    is_noc: bool = False
    dependencies: Optional[Tuple["BaseService", ...]] = None
    compose_image: str
    compose_depends_condition: ComposeDependsCondition = (
        ComposeDependsCondition.STARTED
    )
    compose_healthcheck: Optional[Dict[str, Any]] = None
    compose_command: Optional[str] = None
    compose_entrypoint: Optional[str] = None
    compose_working_dir: Optional[str] = None
    compose_volumes: Optional[List[str]] = None
    compose_volumes_config: Optional[Dict[str, Dict[str, Any]]] = None
    compose_environment: Optional[Dict[str, str]] = None
    compose_extra: Optional[Dict[str, Any]] = None
    service_discovery: Optional[Dict[str, Union[int, Dict[str, Any]]]] = None
    allow_scale: bool = False
    require_slots: bool = False
    expose_http_prefix: Optional[str] = None
    require_http_auth: bool = False
    rewrite_http_prefix: Optional[str] = None

    def iter_dependencies(self: "BaseService") -> Iterable["BaseService"]:
        """
        Iterator yielding the name of dependencies.

        Returns:
            An iterable of strings which represent the names dependencies.
        """
        if self.dependencies:
            yield from self.dependencies

    def get_compose_config(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Dict[str, Any]:
        """
        Generate config for docker-compose target.

        The following functions are used to build config:

        * `get_compose_image` -vto build `image` section.
        * `iter_dependencies` - to build `depends_on` section.
        * `get_compose_working_dir` - to build `working_dir` section.
        * `get_compose_command` - to build `command` section.
        * `get_compose_entrypoint` - to build `entrypoint` section.
        * `get_compose_volumes` - to build `volumes` section.
        * `get_compose_networks` - to build `networks` section.
        * `get_compose_ports` - to build `ports` section.
        * `get_compose_environment` - to build `environments` section.
        * `get_compose_healthcheck` - to build `healthcheck` section.
        * `get_compose_extra` to add the extra parameters to the result.
        * `get_compose_logging` - to build `logging` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            dict of the docker-compose configuration.
        """
        # Basic settings
        r: Dict[str, Any] = {
            "image": self.get_compose_image(config, svc),
            "restart": "no",
        }
        # scale
        if self.allow_scale:
            r["deploy"] = {"replicas": svc.scale if svc else 1}
        # depends_on
        deps = {
            dep.name: {
                "condition": dep.get_compose_depends_condition(
                    config, svc
                ).value
            }
            for dep in self.iter_dependencies()
        }
        if deps:
            r["depends_on"] = deps
        # working_dir
        wd = self.get_compose_working_dir(config, svc)
        if wd:
            r["working_dir"] = wd
        # command
        cmd = self.get_compose_command(config, svc)
        if cmd:
            r["command"] = cmd
        # entrypoint
        entrypoint = self.get_compose_entrypoint(config, svc)
        if entrypoint:
            r["entrypoint"] = entrypoint
        # volumes
        volumes = self.get_compose_volumes(config, svc)
        if volumes:
            r["volumes"] = volumes
        # networks
        networks = self.get_compose_networks(config, svc)
        if networks:
            r["networks"] = {"noc": networks}
        else:
            r["networks"] = ["noc"]
        # ports
        ports = self.get_compose_ports(config, svc)
        if ports:
            r["ports"] = ports
        # environment
        env = self.get_compose_environment(config, svc)
        if env:
            r["environment"] = env
        # healthcheck
        healthcheck = self.get_compose_healthcheck(config, svc)
        if healthcheck:
            r["healthcheck"] = healthcheck
        # logging
        logging = self.get_compose_logging(config, svc)
        if logging:
            r["logging"] = logging
        # extra
        extra = self.get_compose_extra(config, svc)
        if extra:
            r.update(extra)
        # done
        return r

    def get_compose_depends_condition(
        self: "BaseService", config: Config, svc: Optional[ServiceConfig]
    ) -> ComposeDependsCondition:
        """
        Get condition for all dependend services.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Dependency start condition.
        """
        return self.compose_depends_condition

    def get_compose_image(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> str:
        """
        Get docker-compose.yml `image` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Image name.
        """
        try:
            return self.compose_image
        except AttributeError as e:
            msg = "compose_image is not defined"
            raise NotImplementedError(msg) from e

    def get_compose_working_dir(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        """
        Get docker-compose.yml `working_dir` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Working dir, if not empty
        """
        return self.compose_working_dir

    def get_compose_command(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        """
        Get docker-compose.yml `command` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Command, if not empty
        """
        return self.compose_command

    def get_compose_entrypoint(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        """
        Get docker-compose.yml `entrypoint` section.

        Args:
        config: Gufo Thor config instance
        svc: Service's config from `services` part, if any.

        Returns:
        Entrypoint, if not empty
        """
        return self.compose_entrypoint

    def get_compose_networks(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        """
        Get docker-compose.yml `networks` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Networks dict, if not empty
        """
        return None

    def get_compose_volumes(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """
        Get docker-compose.yml `volumes` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            List of volumes config, if not empty.
        """
        return self.compose_volumes

    def get_compose_volumes_config(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get docker-compose.yml global `volumes` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Dict of name -> volumes config
        """
        return self.compose_volumes_config

    def get_compose_ports(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """
        Get docker-compose.yml `ports` section.

        Args:
        config: Gufo Thor config instance
        svc: Service's config from `services` part, if any.

        Returns:
        List of ports config, if not empty
        """
        return None

    def get_compose_environment(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, str]]:
        """
        Get docker-compose.yml `environment` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Dict of environment, if not empty
        """
        return self.compose_environment

    def get_compose_healthcheck(
        self: "BaseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        """
        Get docker-compose.yml `healthcheck` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Dict of healthcheck, if not empty
        """
        return self.compose_healthcheck

    def get_compose_logging(
        self: "BaseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        """
        Get docker-compose.yml `logging` section.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Dict of logging, if not empty
        """
        if docker.logging_driver == "json-file":
            return {"options": {"max-size": "10m", "max-file": "3"}}
        return None

    def get_compose_extra(
        self: "BaseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Any]]:
        """
        Get dict to be merged with compose config/.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Dict of extra settings.
        """
        return self.compose_extra

    def prepare_compose_config(
        self: "BaseService",
        config: Config,
        svc: Optional[ServiceConfig],
        services: List["BaseService"],
    ) -> None:
        """
        Prepare service configs.

        Called after the `get_compose_dirs`

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.
            services: List of all services.
        """
        return

    def get_expose_http_prefix(
        self: "BaseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[str]:
        """
        Iterate over exposed http paths.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.
        """
        return self.expose_http_prefix

    def get_service_discovery(
        self: "BaseService", config: Config, svc: Optional[ServiceConfig]
    ) -> Optional[Dict[str, Union[int, Dict[str, Any]]]]:
        """
        Get name to port mappings for service discovery.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            Service name -> port mappings
        """
        return self.service_discovery

    @staticmethod
    def resolve(services: Iterable[str]) -> List["BaseService"]:
        """
        Resolve services to all dependencies.

        Args:
            services: Iterable of basic services.

        Returns:
            Iterable of all basic services and their dependencies.
        """
        resolved: Set[BaseService] = set()
        wave = {loader[svc] for svc in services}
        while wave:
            current = wave.pop()
            resolved.add(current)
            wave |= set(current.iter_dependencies()) - resolved - wave
        return sorted(resolved, key=operator.attrgetter("name"))

    @staticmethod
    def get_deps_dot() -> str:
        """
        Build dependencies graph in dot format.

        Returns:
            Dependencies graph.
        """
        items: List[Tuple[str, str]] = []
        for svc in sorted(loader.values(), key=lambda x: x.name):
            for d in svc.iter_dependencies():
                items.append((svc.name, d.name))
        r = ["digraph {"] + [f"  {x} -> {y}" for y, x in sorted(items)] + ["}"]
        return "\n".join(r)

    @classmethod
    def render_file(
        cls: Type["BaseService"],
        path: Path,
        tpl: str,
        **kwargs: Union[str, int, List[Any]],
    ) -> None:
        """
        Apply a context to the template and write to file.

        Args:
            path: File path
            tpl: Template name (relative to `gufo.thor.templates`)
            kwargs: Template context
        """
        # Load template
        # Warning: joinpath() accepts only one
        # parameter on Py3.9 and Py3.10
        data = (
            resources.files("gufo.thor")
            .joinpath("templates")
            .joinpath(cls.name)
            .joinpath(tpl)
            .read_text()
        )
        template = jinja2.Template(data)
        data = template.render(**kwargs)
        # Write file
        write_file(path, data)


loader: Loader[BaseService] = Loader[BaseService](
    base="gufo.thor.services", exclude=("base", "noc")
)

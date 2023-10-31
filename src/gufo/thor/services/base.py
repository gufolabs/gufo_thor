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
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

# Gufo Labs modules
from gufo.loader import Loader

# Gufo Thor modules
from ..config import Config, ServiceConfig


class ComposeDependsCondition(Enum):
    STARTED = "service_started"
    HEALTHY = "service_healthy"
    COMPLETED_SUCCESSFULLY = "service_completed_successfully"


class BaseService(ABC):
    """
    Base class for the service declaration.

    Attributes:
        name: Service name
        is_noc: True, if the service is belongs to NOC
        dependencies:
    """

    name: str
    is_noc: bool = False
    dependencies: Optional[Tuple["BaseService", ...]] = None

    @property
    def is_abstract(self: "BaseService") -> bool:
        """
        Check ig the service is abstract.

        Abstract services must be used only as base
        classes for real services.

        Returns:
            True, if service is abstract.
        """
        return hasattr(self, "name")

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
        return ComposeDependsCondition.STARTED

    @abstractmethod
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
        return None

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
        return None

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
        return None

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
        return None

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
        return None

    def get_compose_dirs(
        self: "BaseService", config: "Config", svc: Optional[ServiceConfig]
    ) -> Optional[List[str]]:
        """
        Get list of required directories for the service.

        The required directories should be created before the service
        is been configured. Should be used in conjunction with
        `get_compose_volumes`.

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.

        Returns:
            List of required directories, if not empty.
        """
        return None

    def prepare_compose_config(
        self: "BaseService", config: Config, svc: Optional[ServiceConfig]
    ) -> None:
        """
        Prepare service configs.

        Called after the `get_compose_dirs`

        Args:
            config: Gufo Thor config instance
            svc: Service's config from `services` part, if any.
        """
        return

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
        r = ["digraph {"]
        for svc in loader.values():
            deps = list(svc.iter_dependencies())
            if deps:
                for dep in deps:
                    r.append(f"  {dep.name} -> {svc.name}")
            else:
                r.append(f"  {svc.name}")
        r.append("}")
        return "\n".join(r)


loader: Loader[BaseService] = Loader[BaseService](
    base="gufo.thor.services", exclude=("base", "noc")
)

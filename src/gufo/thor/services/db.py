# ---------------------------------------------------------------------
# Gufo Thor: DBService
# ---------------------------------------------------------------------
# Copyright (C) 2023-26, Gufo Labs
# ---------------------------------------------------------------------
"""DBService definition."""

# Python modules
from importlib import resources

# Third-party modules
import jinja2

# Gufo Thor modules
from .base import BaseService, Role


class DBService(BaseService):
    """Base class for database services that support backup and restore.

    Attributes:
        role: The database role assigned to this service.
    """

    role = Role.DB
    backup_script_template: str | None = None
    restore_script_template: str | None = None
    backup_file_name: str | None = None

    def get_backup_script_name(self) -> str:
        """Get the backup script filename.

        Returns:
            The service-specific backup script filename.
        """
        return f"{self.name}-backup.sh"

    def get_restore_script_name(self) -> str:
        """Get the restore script filename.

        Returns:
            The service-specific restore script filename.
        """
        return f"{self.name}-restore.sh"

    def get_backup_file_name(self) -> str:
        """Get the name of the service backup artifact.

        Returns:
            The service-specific backup filename.
        """
        return self.backup_file_name or f"{self.name}.dump"

    def _render_script_template(self, name: str) -> str:
        """Load and render a backup script template.

        Args:
            name: Template filename under ``templates/backup``.

        Returns:
            Rendered script contents.
        """
        template = (
            resources.files("gufo.thor")
            .joinpath("templates")
            .joinpath("backup")
            .joinpath(name)
            .read_text()
        )
        return jinja2.Template(template).render()

    def get_backup_script(self) -> str:
        """Get the backup script contents.

        Returns:
            The service-specific backup script.
        """
        if self.backup_script_template is None:
            msg = f"Backup for service {self.name} is not implemented"
            raise NotImplementedError(msg)
        return self._render_script_template(self.backup_script_template)

    def get_restore_script(self) -> str:
        """Get the restore script contents.

        Returns:
            The service-specific restore script.
        """
        if self.restore_script_template is None:
            msg = f"Restore for service {self.name} is not implemented"
            raise NotImplementedError(msg)
        return self._render_script_template(self.restore_script_template)

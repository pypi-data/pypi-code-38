"""Service Data refactoring [wip]."""
from typing import List


class ServiceData:
    """Service Data."""

    def __init__(self,
                 name: str,
                 compose: dict,
                 full_name: str,
                 compose_files: List[str],
                 working_dir: str,
                 compose_data: dict,
                 compose_project: dict
                 ):
        """Initialize class."""
        self._name = name
        self._compose = compose
        self._full_name = full_name
        self._compose_files = compose_files
        self._working_dir = working_dir
        self._compose_data = compose_data
        self._compose_project = compose_project

    @property
    def name(self):
        """Name."""
        return self._name

    @property
    def compose(self):
        """Compose."""
        return self._compose

    @property
    def full_name(self):
        """Full Name."""
        return self._full_name

    @property
    def compose_files(self):
        """Compose Files."""
        return self._compose_files

    @property
    def working_dir(self):
        """Working Dir."""
        return self._working_dir

    @property
    def compose_data(self):
        """Compose Data."""
        return self._compose_data

    @property
    def compose_project(self):
        """Compose Project."""
        return self._compose_project

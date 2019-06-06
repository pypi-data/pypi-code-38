"""Main module."""
import os
import sys
from typing import Any, Dict, List

import yaml
from buzio import console
from loguru import logger

from megalus.utils import get_path


class ServiceData:
    """Docker Service Data.

    This class represents all data need for the Docker service.

    Attributes
    ==========
        :param name: Service Name (as per `docker-compose.yml` file)
        :param compose: Compose Project Name (as per `megalus.yml` file)
        :param full_name: Unique name for service (docker name and compose project name)
        :param compose_files: Relative path for all `docker-compose.yml` files for this service.
        :param working_dir: Full Working directory for this service
                (which `.env` and main `docker-compose.yml` files resides)
        :param compose_data: Updated compose data for the Service (from all `dock-compose.yaml` files)
        :param compose_project: Compose project data (as per `megalus.yml` file)
        :param all_compose_data: Update Compose Data for all data (from all `dock-compose.yml` files)

    """

    name: str
    compose: str
    full_name: str
    compose_files: List[str]
    working_dir: str
    compose_data: dict
    compose_project: dict
    all_compose_data: dict

    def __init__(self, service_data: dict) -> None:
        """Initialize class.

        :param service_data: dict parsed from Megalus context
        """
        self.name = service_data['name']
        self.compose = service_data['compose']
        self.full_name = service_data['full_name']
        self.compose_files = service_data['compose_files']
        self.working_dir = service_data['compose_data']
        self.compose_data = service_data['compose_data']
        self.compose_project = service_data['compose_project']
        self.all_compose_data = service_data['all_compose_data']


class Megalus:
    """Megalus main class."""

    def __init__(self, config_file: str, logfile: str) -> None:
        """Initialize class.

        :param config_file: path for megalus config path
        :param logfile: path for save log file
        """
        self.service = None
        self._config_file = config_file
        self.base_path = get_path(os.path.dirname(config_file), '.')
        self.compose_data_list = []  # type: List[dict]
        self._data = {}  # type: Dict[str, Any]
        self.all_services = []  # type: List[dict]
        self.all_composes = {}  # type: dict
        self.logfile = logfile
        self._config_data = {}  # type: dict

    @property
    def config_data(self) -> dict:
        """Return megalus configuration data.

        :return: dict
        """
        if self._config_data:
            return self._config_data

        config_path = os.path.join(
            self.base_path,
            os.path.basename(self._config_file)
        )
        try:
            with open(config_path) as file:
                self._config_data = yaml.safe_load(file.read()) or {}
            return self._config_data
        except FileNotFoundError:
            logger.warning("File {} not found. Skipping...".format(config_path))
            return {}

    def _convert_lists(self, data: dict, key: str) -> None:
        """Convert list to dict inside yaml data.

        Works only for Key=Value lists.

        Example:
            environment:
                - DEBUG=false
            ports:
                - "8090:8080"

        Result:
            environment: {"DEBUG": "false"}
            ports: ['8090:8080']

        """
        if isinstance(data[key], list) and "=" in data[key][0]:
            data[key] = {obj.split("=")[0]: obj.split("=")[-1] for obj in data[key]}
        if isinstance(data[key], dict):
            for k in data[key]:
                self._convert_lists(data[key], k)

    def _load_data_from_override(self, source: dict, target: dict, key: str) -> None:
        """Append override data in self.compose.

        Example Compose::
        ---------------
        core:
            build:
                context: ../core
            image: core
            networks:
                - api1
            environment:
                - DEBUG=false
            ports:
             - "8080:80"

        Example override::
        ----------------
        core:
            build:
                dockerfile: Docker_dev
            depends_on:
                - api
            command: bash -c "python manage.py runserver 0.0.0.0"
            environment:
                DEBUG: "True"
            ports:
                - "9000:80"

        Final Result::
        ------------
        core:
            build:
                context: ../core
                dockerfile: Docker_dev
            depends_on:
                - api
            image: core
            command: bash -c "python manage.py runserver 0.0.0.0"
            environment:
                DEBUG: "True"
            networks:
                - api1
            ports:
             - "8080:80"
             - "9000:80"

        """
        if target.get(key, None):
            if isinstance(source[key], dict):
                for k in source[key]:
                    self._load_data_from_override(
                        source=source[key],
                        target=target[key],
                        key=k
                    )
            else:
                if isinstance(target[key], list) and isinstance(source[key], list):
                    target[key] += source[key]
                else:
                    target[key] = source[key]
        else:
            if isinstance(target, list) and isinstance(source[key], list):
                target[key] += source[key]
            else:
                target[key] = source[key]

    def _get_compose_data_for(self, compose_path: str, compose_files: List[str]) -> dict:
        """Read docker compose files data.

        :return: dict
        """
        try:
            resolved_paths = [
                get_path(os.path.join(compose_path, file), base_path=self.base_path)
                for file in compose_files
            ]

            compose_data_list = []
            for compose_file in resolved_paths:
                with open(compose_file, 'r') as file:
                    compose_data = yaml.safe_load(file.read())
                    for key in compose_data:  # type: ignore
                        self._convert_lists(compose_data, key)
                    compose_data_list.append(compose_data)
            reversed_list = list(reversed(compose_data_list))
            self._data = reversed_list[-1]
            for index, override in enumerate(reversed_list):
                self.override = override
                if index + 1 == len(reversed_list):
                    break
                for key in self.override:
                    self._load_data_from_override(self.override, self._data, key)
            return self._data
        except FileNotFoundError:
            logger.warning("File {} not found. Skipping...".format(compose_file or ""))
            return {}

    def get_services(self) -> None:
        """Build service configuration from yaml files.

        :return: None
        """
        if not self.validate_config_data():
            raise SystemExit(1)
        for compose_project in self.config_data.get('compose_projects', []):
            compose_path = self.config_data['compose_projects'][compose_project]['path']
            compose_files = self.config_data['compose_projects'][compose_project]['files']
            compose_data = self._get_compose_data_for(compose_path, compose_files)
            if not compose_data:
                logger.warning("Project {} has errors. Ignoring...".format(compose_project))
                continue
            self.all_composes.update({compose_project: compose_data})
            for service in compose_data['services']:
                self.all_services.append(
                    {
                        'name': service,
                        'compose': compose_project,
                        'full_name': "{} ({})".format(service, compose_project),
                        'compose_files': compose_files,
                        'working_dir': os.path.dirname(
                            get_path(os.path.join(compose_path, compose_files[0]), self.base_path)),
                        'compose_data': compose_data['services'][service],
                        'compose_project': self.config_data['compose_projects'][compose_project],
                        'all_compose_data': compose_data
                    }
                )

    @staticmethod
    def run_command(command: str) -> bool:
        """Run command inside subprocess.

        :param command: string: command to be run
        :return: bool
        """
        logger.debug("Running command: {}".format(command))
        ret = console.run(command)
        if not ret:
            sys.exit(1)
        return ret

    def find_project(self, project_informed: str) -> dict:
        """Find project from string.

        :param project_informed: string informed in command
        :return: compose project data from yml.
        """
        exact_match = list(self.config_data['compose_projects'].keys()).count(project_informed)
        if exact_match == 1:
            return self.config_data['compose_projects'][project_informed]

        eligible_projects = [
            key
            for key in self.config_data['compose_projects'].keys()
            if project_informed in key
        ]
        if not eligible_projects:
            logger.error("Project not found")
            sys.exit(1)

        elif len(eligible_projects) == 1:
            return self.config_data['compose_projects'][eligible_projects[0]]

        project_key = console.choose(eligible_projects, 'Please select project')
        return self.config_data['compose_projects'][project_key]

    def find_service(self, service_informed: str) -> dict:
        """Find service inside megalus service data.

        :param service_informed: string: docker service informed in command.
        :return: docker service megalus data.
        """
        exact_matches = [
            data
            for data in self.all_services
            if data['name'] == service_informed
        ]
        if len(exact_matches) == 1:
            self.service = exact_matches[0]['name']
            return exact_matches[0]

        eligible_services = [
            eligible_service
            for eligible_service in self.all_services
            if service_informed in eligible_service['name']
        ]
        if not eligible_services:
            logger.error("Service not found")
            sys.exit(1)
        elif len(eligible_services) == 1:
            self.service = eligible_services[0]['name']
            return eligible_services[0]
        else:
            choice_list = [
                data['full_name']
                for data in eligible_services
            ]
            service_name = console.choose(choice_list, 'Please select the service')
        data = [
            data
            for data in eligible_services
            if service_name == data['full_name']
        ][0]
        self.service = data['name']
        return data

    def validate_config_data(self) -> bool:
        """Validate data parsed from megalus.yml file."""
        no_errors = True
        if not self.config_data.get('compose_projects'):
            no_errors = False
            logger.error("Key 'compose_projects' not found in configuration file."
                         " Please check and try again.")
        return no_errors

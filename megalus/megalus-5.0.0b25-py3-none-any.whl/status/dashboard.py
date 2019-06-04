"""Dashboard Module."""
import os
from typing import Optional, Tuple

import docker
from blessed import terminal
from buzio import formatStr
from dashing.dashing import HSplit, Text, VSplit
from docker.models.containers import Container
from git import GitCommandError, InvalidGitRepositoryError, Repo
from tabulate import tabulate

from megalus.check.commands import check_docker_image
from megalus.main import Megalus
from megalus.status.system_watch import megalus_info_widget
from megalus.utils import get_path

client = docker.from_env()

ARROW_UP = u"↑"
ARROW_DOWN = u"↓"
MODIFIED = u"✎"
RUNNING = u"⇄"
WARNING = u"⚠"


class Dashboard:
    """Dashboard class for dashing."""

    def __init__(self, context: Megalus) -> None:
        """Init class.

        :param context: Click context instance
        """
        self.context = context
        self.config_data = context.config_data
        self.all_composes = context.all_composes
        self.base_path = context.base_path

    def get_layout(self, term: terminal, all: bool) -> HSplit:
        """Get dashing terminal layout.

        :param all: show all boxes even if no containers are running
        :param term: Blessed Terminal
        :return: dashing instance
        """
        running_boxes = []
        for project in self.config_data['compose_projects'].keys():
            if project in self.all_composes:
                box = self.get_box(project)
                if all:
                    running_boxes.append(box)
                elif ARROW_DOWN in box.text \
                        or ARROW_UP in box.text \
                        or MODIFIED in box.text \
                        or RUNNING in box.text \
                        or WARNING in box.text:
                    running_boxes.append(box)
        running_boxes.append(megalus_info_widget(self.context))

        boxes = []
        index = 0
        vertical_boxes = int(len(running_boxes) / 4)
        if vertical_boxes > 4:
            vertical_boxes = 4
        while index < len(running_boxes):
            box = running_boxes[index]
            if self.config_data['compose_projects'].get(box.title, {}).get("show_status", {}).get("big", False):
                boxes.append(box)
                index += 1
                continue
            if index + vertical_boxes < len(running_boxes):
                if vertical_boxes == 1:
                    boxes.append(VSplit(running_boxes[index], running_boxes[index + 1]))
                elif vertical_boxes == 2:
                    boxes.append(VSplit(running_boxes[index], running_boxes[index + 1], running_boxes[index + 2]))
                elif vertical_boxes == 3:
                    boxes.append(VSplit(running_boxes[index], running_boxes[index + 1], running_boxes[index + 2],
                                        running_boxes[index + 3]))
                else:
                    boxes.append(VSplit(running_boxes[index], running_boxes[index + 1], running_boxes[index + 2],
                                        running_boxes[index + 3], running_boxes[index + 4]))
                index += (vertical_boxes + 1)
                continue
            if len(running_boxes) - index <= 1:
                boxes.append(running_boxes[index])
                index += 1
            elif len(running_boxes) - index == 2:
                boxes.append(VSplit(running_boxes[index], running_boxes[index + 1]))
                index += 2
            elif len(running_boxes) - index == 3:
                boxes.append(VSplit(running_boxes[index], running_boxes[index + 1], running_boxes[index + 2]))
                index += 3
            else:
                boxes.append(VSplit(running_boxes[index], running_boxes[index + 1], running_boxes[index + 2],
                                    running_boxes[index + 3]))
                index += 4

        ui = HSplit(*boxes, terminal=term, main=True, color=7, background_color=16)
        return ui

    def get_box(self, project: str) -> Text:
        """Return Box widget.

        :param project: project name
        :return: dashing Text widget
        """
        all_services = [
            service
            for service in self.all_composes[project]['services']
            if project in self.all_composes
        ]
        project_path = self.config_data['compose_projects'][project]['path']
        project_path_basename = os.path.basename(project_path)
        ignore_list = self.config_data['compose_projects'][project].get('show_status', {}).get('ignore', [])
        only_list = self.config_data['compose_projects'][project].get('show_status', {}).get('only', [])

        table_header = ['Name', 'Status', 'Ports', 'Git']
        table_lines = []
        for service in all_services:
            if service in ignore_list:
                continue
            if only_list and service not in only_list:
                continue

            container_name, name, service_status = self.get_container_name_and_status(project, project_path_basename,
                                                                                      service)

            service_ports = self.get_container_external_ports(container_name)

            git_status = self.get_service_git_status(project, project_path, service)

            # Append service in table
            table_lines.append([name, service_status, service_ports, git_status])

        table = tabulate(table_lines, table_header)
        return Text(table, color=6, border_color=5, background_color=16,
                    title=project)

    def get_service_git_status(self, project: str, project_path: str, service: str) -> str:
        """Get Service GIT status.

        :param project: Megalus Project Name
        :param project_path: Megalus Project Path
        :param service: Docker service name
        :return: formatted git status
        """
        service_context_path = self.all_composes[project]['services'][service].get('build', {}).get('context', None)
        git_status = formatStr.info('--', use_prefix=False, theme="dark")
        if service_context_path:
            git_status = self.get_git_status(service_context_path, project_path)
        if not git_status:
            git_status = formatStr.info('--', use_prefix=False, theme="dark")
        return git_status

    @staticmethod
    def get_container_external_ports(container_name: str) -> str:
        """Get docker container external ports.

        :param container_name: container name (ex.: megalus_docker_1)
        :return: string
        """
        service_containers_ports = [
            container.attrs['NetworkSettings']['Ports']
            for container in client.containers.list()
            if container_name in container.name
        ]
        external_port_list = []
        for container_data in service_containers_ports:
            for key in container_data:
                if container_data[key] is not None:
                    for port_data in container_data[key]:
                        external_port_list.append(port_data.get("HostPort"))
        service_ports = ",".join(external_port_list) if external_port_list else ""
        return service_ports

    def get_container_name_and_status(
            self, project: str, project_path_basename: str, service: str) -> Tuple[str, str, str]:
        """Get container name and status.

        :param project: megalus Project name
        :param project_path_basename: Docker project path basename
        :param service: Docker project name
        :return:
        """
        container_name = self.all_composes[project]['services'][service].get(
            'container_name', "{}_{}_".format(project_path_basename, service))
        name, service_status = self.get_service_status(service, container_name, project)
        return container_name, name, service_status

    def get_service_status(self, service: str, container_name: str, project: str) -> Tuple[str, str]:
        """Get formatted service name and status.

        :param project: project name
        :param service: service name
        :param container_name: container name for service
        :return: Tuple
        """

        def _get_container_status(container: Container) -> str:
            health_check = container.attrs['State'].get('Health', {}).get('Status')
            return health_check if health_check else container.status

        service_data = [
            data
            for data in self.context.all_services
            if data['name'] == service and data['compose'] == project
        ][0]

        if not check_docker_image(self.context, service_data):
            return (
                formatStr.error(service, use_prefix=False),
                formatStr.error("{} Need Build".format(WARNING), use_prefix=False)
            )

        service_status = [
            _get_container_status(container)
            for container in client.containers.list()
            if container_name in container.name
        ]
        if not service_status:
            return (
                formatStr.info(service, use_prefix=False, theme="dark"),
                formatStr.info("Not Found", use_prefix=False, theme="dark")
            )

        main_status = max(set(service_status), key=service_status.count)
        replicas = len(service_status)
        replicas_in_main_status = service_status.count(main_status)

        if replicas == replicas_in_main_status:
            text = "{}{}".format(
                main_status.title(),
                " x{}".format(replicas) if replicas > 1 else ""
            )
        else:
            text = "{} x{}/{}".format(
                main_status.title(),
                replicas_in_main_status,
                replicas
            )
        if "unhealthy" in main_status:
            formatted_service = formatStr.error(service, use_prefix=False)
            formatted_status = formatStr.error(WARNING + " " + text, use_prefix=False)
        elif "running" in main_status or main_status.startswith("healthy"):
            formatted_service = formatStr.success(service, use_prefix=False)
            formatted_status = formatStr.success(RUNNING + " " + text, use_prefix=False)
        else:
            formatted_service = formatStr.warning(service, use_prefix=False)
            formatted_status = formatStr.warning(WARNING + " " + text, use_prefix=False)
        return formatted_service, formatted_status

    def get_git_status(self, service_path: str, project_path: str) -> Optional[str]:
        """Get formatted git status.

        :param service_path: service build context path
        :param project_path: project base path
        :return: String
        """
        git_path = get_path(os.path.join(project_path, service_path), self.base_path)
        try:
            service_repo = Repo(git_path)
        except InvalidGitRepositoryError:
            return None
        is_dirty = service_repo.is_dirty()
        default_branch = self._get_default_branch(service_repo)
        behind_default = self._get_commits_behind(service_repo, default_branch)
        behind_origin = self._get_commits_behind(service_repo)
        ahead_origin = self._get_commits_ahead(service_repo)
        commits_ahead_text = formatStr.success("{} ".format(ARROW_UP), use_prefix=False) if ahead_origin else ""
        commits_behind_origin_text = formatStr.error("{} {} ".format(ARROW_DOWN, behind_origin),
                                                     use_prefix=False) if behind_origin else ""
        commits_behind_default_text = formatStr.error(
            " {} {} {}".format(ARROW_DOWN, behind_default, default_branch), use_prefix=False) \
            if behind_default and default_branch != service_repo.active_branch.name else ""
        name = service_repo.active_branch.name.split("/")[-1]
        branch_name = formatStr.warning(name, use_prefix=False) if is_dirty else formatStr.info(name, use_prefix=False)
        modified_icon = formatStr.warning("{} ".format(MODIFIED), use_prefix=False) if is_dirty else ""

        text = "{}{}{}{}{}".format(
            commits_ahead_text,
            modified_icon,
            commits_behind_origin_text,
            branch_name,
            commits_behind_default_text
        )
        return text

    @staticmethod
    def _get_default_branch(service_repo: Repo) -> str:
        """Get Default Branch name.

        Retrieve default branch in CVS (ie.: Github)

        :param service_repo: Repo instance
        :return: String
        """
        refs_list = service_repo.refs
        header_ref = [ref for ref in refs_list if "HEAD" in ref.name][0]
        default_ref = [ref for ref in refs_list if ref.commit == header_ref.commit and ref != header_ref]
        return default_ref[0].name.split("/")[-1] if default_ref else ""

    @staticmethod
    def _get_commits(service_repo, log_text):
        try:
            git = service_repo.git
            commit_list = git.log(log_text, oneline=True).split("\n")
            if commit_list and commit_list[0] == "":
                commit_list = []
            return len(commit_list) if commit_list else 0
        except GitCommandError:
            return 0

    def _get_commits_behind(self, service_repo: Repo, default_branch: str = "") -> int:
        """Get commits behind origin.

        Get number of commits actual branch was behind origin.

        :param service_repo: Repo Instance
        :param default_branch: String - Default branch in CVS.
        :return: integer
        """
        if not default_branch:
            default_branch = service_repo.active_branch.name
        log_text = "..origin/{}".format(default_branch)
        return self._get_commits(service_repo, log_text)

    def _get_commits_ahead(self, service_repo: Repo, default_branch: str = "") -> int:
        """Get commits behind origin.

        Get number of commits actual branch was behind origin.

        :param service_repo: Repo Instance
        :param default_branch: String - Default branch in CVS.
        :return: integer
        """
        if not default_branch:
            default_branch = service_repo.active_branch.name
        log_text = "origin/{}..".format(default_branch)
        return self._get_commits(service_repo, log_text)

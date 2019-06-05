#!/usr/bin/env python
from os import path, remove
from semver import VersionInfo
from typing import Dict, List
from swimlane_platform.environment_updater import run_environment_updater_upgrade
from swimlane_platform.lib import ArgsConfigQuestions, DockerComposeFileManager, DockerComposeManager, DockerManager, \
    names, VersionValidator, Configuration, semver_try_parse, \
    debug_function_args, debug_function_return, info_function_start_finish, ValidationException, BaseWithLog
from swimlane_platform.upgrade_steps import Upgrades
import semver
from swimlane_platform.backup.backup import run as backup_run


class SwimlaneUpgrader(BaseWithLog):

    def __init__(self, args):
        # type: (Configuration) -> None
        super(SwimlaneUpgrader, self).__init__(args)
        self._docker_helper = DockerManager(self.logger)

    @info_function_start_finish('Swimlane upgrade.')
    def run(self):
        # type: () -> None
        """
        Main method for upgrading Swimlane installation.
        """
        current_version = self.get_service_version(names.SW_API)
        requested_version = semver.parse_version_info(self.args.version)
        if not self.need_upgrade(current_version, self.args.version):
            self.logger.info('No upgrade applied, current version is bigger or equal to requested one.')
            return
        docker_file = path.join(names.INSTALL_DIR, 'docker-compose.yml')
        old_docker_compose_file = DockerComposeFileManager(self.logger, docker_file)
        old_images = old_docker_compose_file.get_image_tags()
        run_environment_updater_upgrade(self.args.to_dict())
        self.run_incremental_upgrades(current_version, requested_version)
        new_docker_compose_file = DockerComposeFileManager(self.logger, docker_file)
        new_images = new_docker_compose_file.get_image_tags()
        self.remove_old_containers(old_docker_compose_file)
        self.pull_required_images(old_images, new_images)
        self.start_containers(new_docker_compose_file)

    @debug_function_return
    @debug_function_args
    def need_upgrade(self, current_version, upgrade_version):
        # type: (semver.VersionInfo, semver.VersionInfo) -> bool
        """
        Compares versions to determine if upgrade is needed.
        :param current_version: Current version of Swimlane.
        :param upgrade_version: New version of Swimlane.
        :return: True if upgrade needed.
        """
        return current_version < upgrade_version

    @debug_function_return
    @debug_function_args
    def get_service_version(self, service_name):
        # type: (str) -> semver.VersionInfo
        """
        Gets service image version.
        :return: image version
        """
        docker_compose = DockerComposeFileManager(self.logger, path.join(names.INSTALL_DIR, 'docker-compose.yml'))
        image_name = docker_compose.get('services', service_name, 'image')
        return self._get_version_from_image(image_name)

    @info_function_start_finish()
    @debug_function_args
    def pull_required_images(self, old_images, new_images):
        # type: (List[str],List[str]) -> None
        """
        Pulls images from repository (Just as a precaution).
        """
        for old_image in old_images:
            if old_image not in new_images or self._get_version_from_image(old_image) == 'latest':
                self._docker_helper.image_remove(old_image)
                self.logger.info('Removed {image} image.'.format(image=old_image))
        available_images = self._docker_helper.images_get_tags()
        for required_image in new_images:
            if required_image not in old_images or self._get_version_from_image(required_image) == 'latest':
                if required_image not in available_images:
                    self._docker_helper.image_pull(required_image)
                    self.logger.info('Pulled {image} image.'.format(image=required_image))

    @info_function_start_finish('Running incremental upgrades.')
    @debug_function_args
    def run_incremental_upgrades(self, current_version, version):
        # type: (VersionInfo, VersionInfo) -> None
        """
        Runs all incremental upgrades up to a particular version.
        :param current_version: Current version.
        :param version: Target version.
        """
        if not self.need_upgrade(current_version, version):
            return
        upgrade = next((u for u in Upgrades if u.FROM == current_version), None)
        if upgrade:
            upgrade_step = upgrade(self.args)
            upgrade_step.process()
            self.run_incremental_upgrades(upgrade_step.TO, version)

    @debug_function_return
    @debug_function_args
    def _get_version_from_image(self, image_name):
        # type: (str) -> semver.VersionInfo
        """
        Returns the version part of an image.
        :param image_name:
        :return:
        """
        error = ValidationException('Cannot get current version. Cannot determine steps needed.')
        if not image_name:
            raise error
        split = image_name.split(':')
        if len(split) < 1:
            raise error
        tag = split[-1]
        can_parse, version = semver_try_parse(tag)
        if not can_parse:
            if tag == '4.0-7.0.0-beta':
                return VersionInfo(7, 0, 0)
            elif tag == '4.0-7.0.1-beta':
                return VersionInfo(7, 0, 1)
            raise error
        return version

    @info_function_start_finish()
    @debug_function_args
    def remove_old_containers(self, docker_compose_file_manager):
        # type: (DockerComposeFileManager) -> None
        """
        Removes old containers and networks.
        :param docker_compose_file_manager:
        """
        folder, _ = path.split(docker_compose_file_manager.docker_compose_file)
        old_docker_file = path.join(folder, 'docker-compose-temp.yml')
        docker_compose_file_manager.save_as(old_docker_file)
        DockerComposeManager(self.logger, old_docker_file).docker_compose_down()
        remove(old_docker_file)

    @info_function_start_finish()
    @debug_function_args
    def start_containers(self, docker_compose_file_manager):
        # type: (DockerComposeFileManager) -> None
        """
        Starts containers
        :param docker_compose_file_manager: docker compose file manager
        """
        DockerComposeManager(self.logger, docker_compose_file_manager.docker_compose_file).docker_compose_up()


def run(parent_config=None):
    # type: (Dict[str, str]) -> None
    """
    The script run method, that can be called by other script.
    :param parent_config: Additional configuration information collected by parent script.
    """
    questions = [
        {
            'type': 'input',
            'name': 'version',
            'message': 'What version do you want to upgrade to?',
            'validate': VersionValidator
        }
    ]
    config = ArgsConfigQuestions(parent_config)
    config.collect(questions)
    upgrader = SwimlaneUpgrader(config.to_arguments())
    upgrader.run()

from os import path
from semver import VersionInfo
from swimlane_platform.lib import DockerComposeFileManager, DockerImage, env_manager, names, \
    info_function_start_finish, debug_function_args
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
import semver


class UpgradeFrom800To801(UpgradeStep):
    FROM = semver.parse_version_info('8.0.0')  # type: VersionInfo
    TO = semver.parse_version_info('8.0.1')  # type: VersionInfo

    @info_function_start_finish('Upgrade From 8.0.0 To 8.0.1')
    def process(self):
        # type: () -> None
        self.upgrade_image_versions(names.INSTALL_DIR, self.args.dev)
        self.add_requests_ca_bundle_to_env_files(names.INSTALL_DIR)

    @debug_function_args
    def upgrade_image_versions(self, install_dir, dev):
        # type: (str, bool) -> None
        """
        Changes image versions to the new ones
        :param dev: If the images will be pulled from development repository.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        docker_compose = DockerComposeFileManager(self.logger, path.join(install_dir, names.DOCKER_COMPOSE_FILE))
        api_image = DockerImage(image_name='swimlane/swimlane-api', version=str(self.TO)).get(dev)
        docker_compose.set(api_image, 'services', names.SW_API, 'image')
        tasks_image = DockerImage(image_name='swimlane/swimlane-tasks', version=str(self.TO)).get(dev)
        docker_compose.set(tasks_image, 'services', names.SW_TASKS, 'image')
        web_image = DockerImage(image_name='swimlane/swimlane-web', version=str(self.TO)).get(dev)
        docker_compose.set(web_image, 'services', names.SW_WEB, 'image')
        docker_compose.save()

    @debug_function_args
    def add_requests_ca_bundle_to_env_files(self, install_dir):
        """
        Adds the REQUESTS_CA_BUNDLE env variable to the API and Tasks env files. This env var was added
        in version 8.0.0 and is always on.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        key_name = 'REQUESTS_CA_BUNDLE'
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            if key_name not in env_file:
                env_file[key_name] = '/etc/ssl/certs'
                env_manager.write_dict(file_path, env_file)

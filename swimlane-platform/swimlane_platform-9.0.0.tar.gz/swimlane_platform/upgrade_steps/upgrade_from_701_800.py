from os import path, remove
from semver import VersionInfo
from swimlane_platform.enable_ssl import run as enable_ssl_run
from swimlane_platform.lib import DockerComposeFileManager, DockerImage, env_manager, names, Configuration, \
    info_function_start_finish, debug_function_args, DockerManager
from swimlane_platform.upgrade_steps.upgrade_step import UpgradeStep
import shutil
from swimlane_platform.add_file_encryption_key import run as run_add_file_encryption_key
import semver


class UpgradeFrom701To800(UpgradeStep):
    FROM = semver.parse_version_info('7.0.1')  # type: VersionInfo
    TO = semver.parse_version_info('8.0.0')  # type: VersionInfo

    @info_function_start_finish('Upgrade From 7.0.1 To 8.0.0')
    def process(self):
        # type: () -> None
        self.remove_neo4j(names.INSTALL_DIR)
        enable_ssl_run(self.args.to_dict())
        self.add_swimlane_prefix(names.INSTALL_DIR)
        self.upgrade_image_versions(names.INSTALL_DIR, self.args.dev)
        self.add_encryption_keys(self.args)
        self.add_default_ha(names.INSTALL_DIR)
        self.add_dashed_aliases(names.INSTALL_DIR)
        self.remove_pip_volume()
        self.change_restart_policy(names.INSTALL_DIR)
        self.add_pfx_password_template_to_env_files(names.INSTALL_DIR)

    @debug_function_args
    def remove_neo4j(self, install_dir):
        # type: (str) -> None
        """
        Removes all mentions of neo4j from infrastructure.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        # Modify env files.
        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            new_env_file = dict((key, value) for key, value in env_file.items() if 'Neo4j' not in key)
            wait_for = env_file.get('WAIT_FOR').split(',')
            new_wait_for = [service for service in wait_for if names.SW_NEO_J not in service]
            new_env_file['WAIT_FOR'] = ','.join(new_wait_for)
            env_manager.write_dict(file_path, new_env_file)
        # Remove unneeded env file
        neo4j_env_file = path.join(secrets_dir, '.neo4j-env')
        if path.exists(neo4j_env_file):
            remove(neo4j_env_file)
        # Modify docker-compose file.
        docker_compose = DockerComposeFileManager(self.logger, path.join(install_dir, names.DOCKER_COMPOSE_FILE))
        docker_compose.get('services').pop(names.SW_NEO_J, None)
        docker_compose_override = DockerComposeFileManager(self.logger, path.join(install_dir, names.DOCKER_COMPOSE_OVERRIDE_FILE))
        docker_compose_override.get('services').pop(names.SW_NEO_J, None)
        docker_compose_override.save()
        for service_name in [names.SW_API, names.SW_TASKS]:
            docker_compose.subtract_from_list(names.SW_NEO_J, 'services', service_name, 'depends_on')
        docker_compose.get('volumes').pop('neo4jdb', None)
        docker_compose.save()

    @debug_function_args
    def add_swimlane_prefix(self, install_dir):
        # type: (str) -> None
        """
        Adds SWIMLANE_ prefix to dotnet config variables. Made for better separation and management of them.
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        swimlane_prefix = 'SWIMLANE_'

        def append_prefix(key):
            # type: (str) -> str
            return swimlane_prefix + key if '__' in key and not key.startswith(swimlane_prefix) else key

        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            new_env_file = dict((append_prefix(key), value) for key, value in env_file.items())
            env_manager.write_dict(file_path, new_env_file)

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
        docker_compose.set('mongo:4.0.5', 'services', names.SW_MONGO, 'image')
        docker_compose.save()

    @debug_function_args
    def add_encryption_keys(self, args):
        # type: (Configuration) -> None
        """
        Implements changes to the secrets.
        :param args: Application arguments.
        """
        # Rename .txt to .key
        secrets_dir = path.join(names.INSTALL_DIR, names.SECRETS_SUB_FOLDER)
        old_database_encryption_key = path.join(secrets_dir, 'database_encryption_key.txt')
        if path.exists(old_database_encryption_key):
            new_database_encryption_key = path.join(secrets_dir, 'database_encryption.key')
            shutil.move(old_database_encryption_key, new_database_encryption_key)
            docker_compose = DockerComposeFileManager(self.logger, path.join(names.INSTALL_DIR, names.DOCKER_COMPOSE_FILE))
            docker_compose.set(new_database_encryption_key, 'secrets', 'database_encryption_key', 'file')
            docker_compose.save()
        run_add_file_encryption_key(dict(args.__dict__))

    @debug_function_args
    def add_default_ha(self, install_dir):
        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            if 'SWIMLANE_EnableHA' not in env_file:
                env_file['SWIMLANE_EnableHA'] = 'false'
            env_manager.write_dict(file_path, env_file)

    @debug_function_args
    def add_dashed_aliases(self, install_dir):
        docker_compose = DockerComposeFileManager(self.logger, path.join(install_dir, names.DOCKER_COMPOSE_FILE))
        for service in [names.SW_API, names.SW_WEB]:
            alias_path = ['services', service, 'networks', 'internal_network', 'aliases']
            docker_compose.append_or_create_list(service.replace('_', '-'), *alias_path)
        docker_compose.save()

    @debug_function_args
    def remove_pip_volume(self):
        """
        Removes the pip volume so it can be rebuilt by the application. Preinstalled packages were removed
        from the volume in version 8.0.0.
        """
        docker_manager = DockerManager(self.logger)
        docker_manager.volume_remove('pip')

    @debug_function_args
    def change_restart_policy(self, install_dir):
        """
        The restart policy for swimlane containers was changed from "on-failure:5" to "unless-stopped" in version 8.0.0
        """
        docker_compose = DockerComposeFileManager(self.logger, path.join(install_dir, names.DOCKER_COMPOSE_FILE))
        for service in [names.SW_API, names.SW_WEB, names.SW_TASKS]:
            alias_path = ['services', service, 'restart']
            docker_compose.set('unless-stopped', *alias_path)
        docker_compose.save()

    @debug_function_args
    def add_pfx_password_template_to_env_files(self, install_dir):
        """
        Adds the commented out SWIMLANE_PfxPassword env variable to the API and Tasks env files
        :param install_dir: Root folder for installation. Where docker-compose resides.
        """
        secrets_dir = path.join(install_dir, names.SECRETS_SUB_FOLDER)
        env_files = [names.API_ENV_FILE, names.TASKS_ENV_FILE]
        key_name = '#{}_PfxPassword'.format(names.SWIMLANE_PREFIX)
        for file_path in (path.join(secrets_dir, file_name) for file_name in env_files):
            env_file = env_manager.read_dict(file_path)
            if any(key in env_file for key in (key_name, key_name[1:])):
                return
            
            env_file[key_name] = '<password-placeholder>'
            env_manager.write_dict(file_path, env_file)

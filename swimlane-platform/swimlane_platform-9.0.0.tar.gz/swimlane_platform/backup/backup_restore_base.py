from __future__ import print_function
from os import path, walk, unlink, makedirs
import shutil
from datetime import datetime
import docker
from typing import Union
from swimlane_platform.lib import debug_function_return, debug_function_args, DockerManager, names, \
    ValidationException, Configuration, parse_env_variables_to_dict, ArgsConfigQuestions, PyMongoManager
from swimlane_platform.lib.base_with_log import BaseWithLog


class MongoConnection:
    host = None
    port = None
    user_name = None
    password = None
    ssl = False
    pem_file = None

    def __init__(self, py_mongo_manager=None, uri=None, configuration=None, pem_file=None):
        # type: (Union[PyMongoManager, None], Union[str, None], Union[Configuration, None], Union[str, None]) -> None
        if uri and configuration:
            raise ValidationException("MongoCollection accepts either uri or configuration, not both.")
        elif uri:
            self.from_py_mongo(py_mongo_manager, uri, pem_file)
        elif configuration:
            self.from_configuration(configuration, pem_file)
        else:
            raise ValidationException("MongoCollection accepts either uri or configuration, none were provided.")

    def from_py_mongo(self, py_mongo_manager, uri, pem_file):
        py_mongo = py_mongo_manager.parse_mongo_uri(uri)
        host, port = py_mongo.get('nodelist')[0]
        self.host = host
        self.port = port
        self.user_name = py_mongo.get('username')
        self.password = py_mongo.get('password')
        self.ssl = 'options' in py_mongo and py_mongo['options'].get('ssl')
        self.pem_file = pem_file

    def from_configuration(self, configuration, pem_file):
        self.host = configuration.mongo_host
        self.port = configuration.mongo_port
        self.user_name = configuration.mongo_user_name
        self.password = configuration.mongo_password
        self.ssl = bool(pem_file)
        self.pem_file = pem_file


class BackupRestoreBase(BaseWithLog):
    BACKUP_IMAGE = None
    DB_SWIMLANE = 'Swimlane'
    DB_SWIMLANE_HISTORY = 'SwimlaneHistory'
    BACKUP_FOLDER = '/backup'
    CERT_FOLDER = '/certs'

    def __init__(self, args):
        # type: (Configuration) -> None
        super(BackupRestoreBase, self).__init__(args)
        self.client = docker.from_env()
        self.docker_manager = DockerManager(self.logger)
        backup_image_name = 'swimlane/swimlane-backup:latest'
        self.BACKUP_IMAGE = 'nexus.swimlane.io:5000/' + backup_image_name if args.dev else backup_image_name

    @debug_function_return
    @debug_function_args
    def clear_directory(self, folder_path):
        # type: (str) -> None
        """
        Removes all files from the directory.
        :param folder_path: Directory
        """
        for root, dirs, files in walk(folder_path):
            for f in files:
                unlink(path.join(root, f))
            for d in dirs:
                shutil.rmtree(path.join(root, d))

    @debug_function_return
    @debug_function_args
    def get_archive_name(self, backup_dir, archive=None):
        # type: (str, str) -> (str, str)
        """
        Returns file name for new archive.
        :param archive: Archive name if known (for run)
        :param backup_dir: Location on host to put backups.
        :return: File name
        """
        name = archive if archive else datetime.now().strftime("%Y%m%d-%H%M")
        remote = '/'.join([self.BACKUP_FOLDER, name])
        local = path.join(backup_dir, name)
        if not path.exists(local):
            makedirs(local)
        return local, remote

    @debug_function_return
    def get_certificate_location(self):
        # type: () -> Union[str, None]
        mongo_container = self.docker_manager.container_get(names.SW_MONGO)
        if not mongo_container:
            raise ValidationException('Cannot find MongoDb container on the system.')
        mongo_container_attr = mongo_container.attrs
        cmd = mongo_container_attr.get('Config', {}).get('Cmd')
        pem_key_file = '--sslPEMKeyFile'
        if not cmd or pem_key_file not in cmd:
            return None
        pem_switch = cmd.index(pem_key_file)
        if len(cmd) < pem_switch + 2:
            return None
        pem_secret_location = cmd[pem_switch + 1]
        for mount in mongo_container_attr.get('Mounts', []):
            if mount.get('Destination') == pem_secret_location:
                local_file_path = mount.get('Source')
                if local_file_path:
                    local_file_path = path.abspath(local_file_path)
                    if path.exists(local_file_path):
                        return local_file_path
                    else:
                        self.logger.warn('MongoDB pem file was found in container, but not on the file system.')
        return None

    @debug_function_args
    def validate_backup_exists(self, full_archive_path, *backups):
        # type: (str, str) -> None
        """
        Validates if individual backups are actually present in the folder.
        :param full_archive_path: Backup folder.
        :param backups: Names of backups expected to be in the folder.
        """
        for name in backups:
            if not path.exists(path.join(full_archive_path, name)):
                raise ValidationException("{name} backup is missing".format(name=name))

    def report_archive_name(self, archive_name):
        # type: (str) -> None
        self.logger.info(
            'Backup completed successfully. Archive name: {archive_name}'.format(archive_name=archive_name))

    @debug_function_return
    @debug_function_args
    def get_mongo_connection(self):
        # type: () -> MongoConnection
        """
        Acquires Mongo Connection either form API container or Questions
        :return: Mongo Connection
        """
        env = parse_env_variables_to_dict(self.docker_manager.container_get_dotnet_env(names.SW_API))
        pem_file = self.get_certificate_location()
        if not pem_file:
            questions = [
                {
                    'type': 'input',
                    'name': 'mongo_certificate',
                    'message': 'Location of Mongo certificate',
                    'validate': lambda a: path.exists(a['mongo_certificate'])
                }
            ]
            config_manager = ArgsConfigQuestions(self.args.to_dict())
            config_manager.collect(questions)
            pem_file = config_manager.to_arguments().mongo_certificate
        if names.DOT_NET_SWIMLANE_CONN_KEY not in env:
            questions = [
                {
                    'type': 'input',
                    'name': 'mongo_host',
                    'message': 'Host name of mongo server',
                    'default': names.SW_MONGO
                },
                {
                    'type': 'input',
                    'name': 'mongo_port',
                    'message': 'Port of mongo server',
                    'default': 27017
                },
                {
                    'type': 'input',
                    'name': 'mongo_user_name',
                    'message': 'Mongo user name'
                },
                {
                    'type': 'input',
                    'name': 'mongo_password',
                    'message': 'Mongo password'
                }
            ]
            config_manager = ArgsConfigQuestions(self.args.to_dict())
            config_manager.collect(questions)
            configuration = config_manager.to_arguments()
            return MongoConnection(configuration=configuration, pem_file=pem_file)
        else:
            return MongoConnection(py_mongo_manager=(PyMongoManager(self.logger)),
                                   uri=env[names.DOT_NET_SWIMLANE_CONN_KEY],
                                   pem_file=pem_file)

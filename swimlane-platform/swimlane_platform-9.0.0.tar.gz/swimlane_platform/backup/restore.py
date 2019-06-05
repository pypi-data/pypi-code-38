from os import path
from swimlane_platform.backup.backup_restore_base import BackupRestoreBase
from swimlane_platform.lib import debug_function_args, names, ExpectedException, PathExistsValidator, \
    AnswerRequiredValidator, ArgsConfigQuestions, info_function_start_finish


class Restore(BackupRestoreBase):

    @info_function_start_finish('Swimlane restore.')
    def run(self):
        """
        Main method.
        """
        host_archive, docker_archive = self.get_archive_name(self.args.backup_dir, self.args.archive)
        # noinspection PyBroadException
        try:
            self.docker_manager.containers_exists_validate(names.SW_TASKS, names.SW_WEB, names.SW_API, names.SW_MONGO)
            self.validate_backup_exists(host_archive,
                                        '{db}.gz'.format(db=self.DB_SWIMLANE),
                                        '{db}.gz'.format(db=self.DB_SWIMLANE_HISTORY))
            self.docker_manager.containers_run(self.docker_manager.container_stop, names.SW_WEB, names.SW_TASKS,
                                               names.SW_API)
            self.restore_mongo(docker_archive, self.DB_SWIMLANE)
            self.restore_mongo(docker_archive, self.DB_SWIMLANE_HISTORY, True)
            self.remove_pip_volume()
        finally:
            self.docker_manager.containers_run(self.docker_manager.container_start, names.SW_API, names.SW_TASKS,
                                               names.SW_WEB)

    @debug_function_args
    def restore_mongo(self, archive, database, auto_remove=False):
        # type: (str, str, bool) -> None
        """
        Restore MongoDb database.
        :rtype: None
        :param archive:
        :param database:
        :param auto_remove:
        """
        self.logger.info("Started MongoDb {db} run.".format(db=database))
        mongo_connection = self.get_mongo_connection()
        folder, cert_name = path.split(mongo_connection.pem_file)
        drop_command = 'mongo' \
                       ' {db}' \
                       ' --host {host}' \
                       ' --username {mongo_user}' \
                       ' --password {mongo_password}' \
                       ' --eval "db.dropDatabase();"' \
                       ' --ssl' \
                       ' --sslPEMKeyFile {cert_folder}/{cert_name}' \
                       ' --sslAllowInvalidCertificates'.format(db=database,
                                                               host=mongo_connection.host,
                                                               mongo_user=mongo_connection.user_name,
                                                               mongo_password=mongo_connection.password,
                                                               cert_name=cert_name,
                                                               cert_folder=self.CERT_FOLDER)
        restore_command = 'mongorestore' \
                          ' --host {host}' \
                          ' --gzip' \
                          ' --ssl' \
                          ' --drop' \
                          ' --db {db}' \
                          ' --archive={archive}/{db}.gz' \
                          ' --username {mongo_user}' \
                          ' --password {mongo_password}'\
                          ' --ssl' \
                          ' --sslPEMKeyFile {cert_folder}/{cert_name}' \
                          ' --sslAllowInvalidCertificates'.format(host=mongo_connection.host,
                                                                  db=database,
                                                                  mongo_user=mongo_connection.user_name,
                                                                  mongo_password=mongo_connection.password,
                                                                  archive=archive,
                                                                  cert_name=cert_name,
                                                                  cert_folder=self.CERT_FOLDER)
        volumes = {
            self.args.backup_dir: {'bind': self.BACKUP_FOLDER, 'mode': 'rw'},
            folder: {'bind': self.CERT_FOLDER, 'mode': 'rw'}
        }
        command = ['/bin/bash', '-c', '{drop}; {restore}'.format(drop=drop_command, restore=restore_command)]
        network = self.docker_manager.container_get_network_name(names.SW_MONGO)
        logs = self.client.containers.run(self.BACKUP_IMAGE,
                                          command=command,
                                          stderr=True,
                                          stream=True,
                                          auto_remove=auto_remove,
                                          volumes=volumes,
                                          network=network)
        for log in logs:
            self.logger.verbose(log)
        self.logger.info("Finished MongoDb {db} restore.".format(db=database))

    @info_function_start_finish()
    def remove_pip_volume(self):
        # type: () -> None
        """
        Remove pip volume.
        """
        self.docker_manager.volume_remove('pip')


def run(parent_config):
    questions = [
        {
            'type': 'input',
            'name': 'backup_dir',
            'message': 'Folder where backups are stored',
            'validate': PathExistsValidator
        },
        {
            'type': 'input',
            'name': 'archive',
            'message': 'Name of the archive to run from',
            'validate': AnswerRequiredValidator
        }
    ]
    config_manager = ArgsConfigQuestions(parent_config)
    config_manager.collect(questions)
    restore = Restore(config_manager.to_arguments())
    restore.run()

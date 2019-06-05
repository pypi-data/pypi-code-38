import shutil
from os import path
from swimlane_platform.backup.backup_restore_base import BackupRestoreBase
from swimlane_platform.lib import ArgsConfigQuestions, PathExistsValidator, ExpectedException, \
    debug_function_args, names, info_function_start_finish


class Backup(BackupRestoreBase):

    @info_function_start_finish('Swimlane backup.')
    def run(self):
        # type: () -> None
        """
        Main method.
        """
        local, remote = self.get_archive_name(self.args.backup_dir)
        # noinspection PyBroadException
        try:
            self.docker_manager.containers_run(self.docker_manager.container_stop, names.SW_WEB, names.SW_TASKS,
                                               names.SW_API)
            self.backup_mongo(remote, self.DB_SWIMLANE)
            self.backup_mongo(remote, self.DB_SWIMLANE_HISTORY, True)
            self.report_archive_name(remote)
        except Exception:
            shutil.rmtree(local)
            raise
        finally:
            self.docker_manager.containers_run(self.docker_manager.container_start, names.SW_API, names.SW_TASKS,
                                               names.SW_WEB)

    @debug_function_args
    def backup_mongo(self, archive, database, auto_remove=False):
        # type: (str, str, bool) -> None
        """
        Backup MongoDb database.
        :param auto_remove: Remove container after image run.
        :param archive: This specific run folder. Archive.
        :param database: Database name.
        """
        self.logger.info("Started MongoDb {db} backup.".format(db=database))
        mongo_connection = self.get_mongo_connection()
        folder, cert_name = path.split(mongo_connection.pem_file)
        command = 'mongodump' \
                  ' --host {host}' \
                  ' --gzip' \
                  ' --excludeCollectionsWithPrefix hangfire' \
                  ' --db {db}' \
                  ' --archive={archive}/{db}.gz' \
                  ' --username {mongo_user}' \
                  ' --password {mongo_password}' \
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
        self.logger.info("Finished MongoDb {db} backup.".format(db=database))


def run(parent_config):
    questions = [
        {
            'type': 'input',
            'name': 'backup_dir',
            'message': 'Folder for storing backups',
            'validate': PathExistsValidator
        }
    ]
    config_manager = ArgsConfigQuestions(parent_config)
    config_manager.collect(questions)
    backup = Backup(config_manager.to_arguments())
    backup.run()

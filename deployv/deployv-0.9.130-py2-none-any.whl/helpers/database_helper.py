from deployv.base import postgresv
from deployv.helpers import backup, utils
from deployv.base import errors
import os
import logging
import zipfile

_logger = logging.getLogger(__name__)


class DatabaseHelper(object):

    def __init__(self, db_config):
        self.db_config = db_config

    @staticmethod
    def get_helper(use_template=False):
        if use_template:
            instance = CopyDatabase
        else:
            instance = RestoreBackup
        return instance

    def search_candidate(self, *args, **kwargs):
        raise errors.MethodNotImplemented('The class you are instantiating does'
                                          ' not have this method implemented')

    def create_database(self, *args, **kwargs):
        raise errors.MethodNotImplemented('The class you are instantiating does'
                                          ' not have this method implemented')


class CopyDatabase(DatabaseHelper):

    def search_candidate(self, customer_id):
        original_prefix = 'original_{cid}'.format(cid=customer_id)
        postgres = postgresv.PostgresShell(self.db_config)
        databases = postgres.list_databases()
        customer_originals = []
        for database in databases:
            if database.get('name').startswith(original_prefix):
                customer_originals.append(database.get('name'))
        customer_originals.sort()
        _logger.info('Original databases found: %s', customer_originals)
        if not customer_originals:
            return (False,
                    'Could not find any original database for'
                    ' the customer {cid}'.format(cid=customer_id))
        latest_original = customer_originals[-1]
        _logger.info('Will use: %s', latest_original)
        return (True, latest_original)

    def create_database(self, source, db_name, db_owner, db_owner_password):
        """ Creates a new database copy of another database

        :param database: Name of the database that will be copied
        :return: Name of the new database copy of the one passed as parameter
        """
        db_config = self.db_config.copy()
        db_config.update({"db_owner": db_owner, "db_owner_password": db_owner_password})
        postgres = postgresv.PostgresShell(db_config)
        postgres.drop(db_name, force=True)
        user = db_config.get('user')
        db_config.update({'dbname': 'template1', 'isolation_level': True})
        with postgresv.PostgresConnector(db_config) as db:
            db.execute("CREATE DATABASE \"{new}\" OWNER {owner} TEMPLATE \"{template}\""
                       .format(new=db_name, owner=db_config.get('user'),
                               template=source))
        db_config.update({'dbname': db_name, 'user': db_owner,
                          'password': db_owner_password})
        with postgresv.PostgresConnector(db_config) as db:
            db.execute("REASSIGN OWNED BY {owner} TO {user}"
                       .format(owner=db_owner, user=user))
        return (True, db_name)


class RestoreBackup(DatabaseHelper):

    def search_candidate(self, backup_src, customer_id):
        return self._check_backup_folder(backup_src, customer_id)

    def create_database(self, dest_dir, db_name, db_owner, db_owner_password, **kwargs):
        dump = self._get_dump(dest_dir)
        jobs = False
        if not dump:
            return (False, 'Could not find any dump in the folder {dest}'.format(dest=dest_dir))
        if not os.path.isdir(dump) and kwargs.get("jobs"):
            _logger.warn('the backup was not created with parallel jobs')
        elif os.path.isdir(dump):
            jobs = kwargs.get("jobs") or 5
        self._restore_backup(dump, db_name, db_owner, db_owner_password, jobs=jobs)
        return (True, db_name)

    def _check_backup_folder(self, backup_src, customer_id):
        valid_backups = ['dump.sql', 'database_dump.sql', 'database_dump.b64', "database_dump"]
        if not backup_src or not os.path.exists(backup_src):
            _logger.warn('Path %s does not exists', backup_src and backup_src or '')
            res = (False, 'No backup path supplied or does not exits')
        elif os.path.isdir(backup_src):
            if any([bkp for bkp in valid_backups if bkp in os.listdir(backup_src)]):
                res = (True, backup_src)
            else:
                database_file = backup.search_backup(backup_src, customer_id)
                if not database_file:
                    res = (False, 'Not found any candidate backup to be restored')
                else:
                    res = (True, database_file)
        else:
            res = (True, backup_src)
        return res

    def _get_dump(self, dest_dir):
        dump_name = os.path.join(dest_dir, 'database_dump.sql')
        if os.path.exists(os.path.join(dest_dir, 'dump.sql')):
            dump_name = os.path.join(dest_dir, 'dump.sql')
        if os.path.isdir(os.path.join(dest_dir, 'database_dump')):
            dump_name = os.path.join(dest_dir, 'database_dump')
        if os.path.exists(os.path.join(dest_dir, 'database_dump.b64')):
            _logger.debug('Is a backup generated with WS')
            destination_file = os.path.join(dest_dir, 'backup.zip')
            if 'dump.sql' in os.listdir(dest_dir):
                dump_name = os.path.join(dest_dir, 'dump.sql')
            else:
                if 'backup.zip' not in os.listdir(dest_dir):
                    utils.decode_b64_file(
                        os.path.join(dest_dir, 'database_dump.b64'), destination_file)
                if 'backup.zip' in os.listdir(dest_dir):
                    zfile = zipfile.ZipFile(destination_file)
                    _logger.info('Unzipping backup')
                    try:
                        zfile.extractall(dest_dir)
                    except IOError as error:
                        _logger.error(
                            'Could not extract database_dump.b64: %s', str(error))
                        return None
                    dump_name = os.path.join(dest_dir, 'dump.sql')
        return dump_name

    def _restore_backup(self, dump_name, database_name, db_owner, db_owner_password,
                        jobs=False):
        self.db_config.update({'database': database_name, 'owner': db_owner,
                               'owner_password': db_owner_password})
        postgres = postgresv.PostgresShell(self.db_config)
        postgres.drop(database_name, force=True)
        postgres.restore(database_name, dump_name, jobs=jobs)
        return True

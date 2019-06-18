# coding: utf-8

import logging
import os
import shlex
import spur
import psycopg2
import psycopg2.extras
from psycopg2 import OperationalError, ProgrammingError
from deployv.base import errors
from deployv.helpers import utils

logger = logging.getLogger(__name__)  # pylint: disable=C0103


class PostgresConnector(object):
    """A simple helper to perform a postgres connection and execute simple sql sentences.
    """

    __conn = None
    __cursor = None
    __allowed_keys = ['host', 'port', 'dbname', 'user', 'password']
    __str_conn = ''

    def __init__(self, config=None):
        if config is None:
            config = {}
            # TODO: generate proper connection str from config dict
            # str_conn = "dbname=postgres"  # Error message or connect?
        for key, value in config.items():
            if value is not None and key in self.__allowed_keys:
                self.__str_conn = '%s %s=%s' % (self.__str_conn, key, value)
            elif key == 'dbname' and value is None:
                self.__str_conn = '%s %s=%s' % (
                    self.__str_conn, 'dbname', 'postgres')
        logger.debug('Connection string: %s', self.__str_conn)
        try:
            logger.debug('Stabilishing connection with db server')
            self.__conn = psycopg2.connect(self.__str_conn)
            if config.get('isolation_level', False):
                self.__conn.set_isolation_level(0)
            self.__cursor = self.__conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor)
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:
            # TODO: log this then raise
            logger.debug(
                'Connection to database not established: %s', str(error))
            # Proper cleanup
            self.disconnect()
            raise

    def execute(self, sql_str, *args):
        """This method basically wraps *execute* cursor method from psycopg2.

        See `passing parameters to sql
        <http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries>`_
        for more information.

        :param sql_str: Sql to be executed.
        :type sql_str: str
        :param args: Args, all will be passed to `cursor.execute
            <http://initd.org/psycopg/docs/cursor.html#cursor.execute>`_.
        :type args: tuple
        :returns: A dict if a select was performed. Bool if update/insert.
        :rtype: dict or bool
        """
        change = sql_str.lower().startswith((
            'insert into', 'update', 'create', 'delete', 'alter', 'reassign', 'grant'))
        try:
            logger.debug('SQL: %s', sql_str)
            self.__cursor.execute(sql_str, *args)
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception:
            self.__conn.rollback()
            raise
        if change:
            self.__conn.commit()
        return utils.copy_list_dicts(self.__cursor) if not change else True

    def check_config(self):
        """Check if can connect to PostgreSQL server with the provided configuration.

        :returns: If succeeded or not.
        :rtype: bool
        """
        try:
            logger.debug('')
            res = self.execute("select version();")
            logger.debug('Postgres returned: %s', res)
        except (KeyboardInterrupt, errors.GracefulExit):
            raise
        except Exception as error:  # pylint: disable=W0703
            logger.error('PostgreSQL connection test failed %s',
                         str(error))
            return False
        return True

    def disconnect(self):
        if self.__cursor:
            logger.debug('disconnect: closing cursor')
            self.__cursor.close()
        if self.__conn:
            logger.debug('disconnect: closing connection')
            self.__conn.close()

    def __del__(self):
        self.disconnect()

    def __exit__(self, type, value, traceback):  # pylint: disable=W0622
        self.disconnect()

    def __enter__(self):
        return self


class PostgresShell(object):
    """This class is used to perform some Postgres operations that generally are done in the
    console.

    For example:

    * pg_dump
    * pg_restore
    * psql
    * dropdb

    All keys passed in the dictionary to the constructor must be in `libpq keys style
    <http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-PARAMKEYWORDS>`_.
    """

    __defaults = {'dbname': 'postgres'}
    __formats = {'host': '-h {host}', 'port': '-p {port}', 'user': '-U {user}'}

    def __init__(self, config):

        self.__config = config
        for key, value in self.__defaults.items():
            if not self.__config.get(key, False):
                self.__config.update({key: value})

    def __format_cmd(self, cmd, items):
        res = cmd
        for key, value in self.__formats.items():
            if key in items:
                res = '%s %s' % (res, value)
        return res

    def list_databases(self):
        sql = '''SELECT d.datname as "name",
                    u.usename as "owner",
                    pg_catalog.pg_encoding_to_char(d.encoding) as "encoding"
                    FROM pg_catalog.pg_database d
                    LEFT JOIN pg_catalog.pg_user u ON d.datdba = u.usesysid
                    ORDER BY 1;'''

        with PostgresConnector(self.__config) as db:
            res = db.execute(sql)
        return res

    def terminate_sessions(self, db_name, owner, owner_passwd):
        """operation. terminate sessions of users in database

        :param db_name: Database name to terminate session.
        :type db_name: str
        :param owner: User name with permission superuser.
        :type owner: str
        :param owner_passwd: Password of owner superuser.
        :type owner_passwd: str
        :returns: None
        """
        config = self.__config.copy()
        config.update({'dbname': "template1", 'user': owner,
                       'password': owner_passwd})
        sql = (("SELECT pg_terminate_backend(pid) from pg_stat_activity "
               "WHERE pid <> pg_backend_pid() AND datname = '{dbname}'")
               .format(dbname=db_name))
        try:
            with PostgresConnector(config) as db:
                db.execute(sql)
        except (ProgrammingError, OperationalError) as error:
            logger.error(("Failed to end the connections to the database %s"),
                         utils.get_error_message(error))

    def dump(self, database, destiny_file, jobs=False):
        """Dumps database using pg_dump in sql format.

        :param database: database to be dumped.
        :type database: str
        :param destiny_file: Filename with full path where the dump will be stored.
        :type destiny_file: str
        :returns: The full dump path and name with .sql extension if success.
        :rtype: str or None
        """
        logger.debug("Dumping database %s into %s folder",
                     database, destiny_file)
        if self.__config.get('password', False):
            os.environ['PGPASSWORD'] = self.__config.get('password')
        self.__config.update({'dbname': database})
        dump_cmd = 'pg_dump {dbname} -O -x -f {0}'
        if jobs:
            self.__config.update({'num': jobs})
            dump_cmd = 'pg_dump -j {num} -F d {dbname} -f {0} -x'
        dump_cmd = self.__format_cmd(dump_cmd, self.__config)
        dump_cmd = dump_cmd.format(destiny_file, **self.__config)
        logger.debug('Dump command: %s', dump_cmd)
        shell = spur.LocalShell()
        try:
            shell.run(shlex.split(dump_cmd))
        except spur.results.RunProcessError as error:
            str_error = utils.decode(error.stderr_output)
            if 'does not exist' in str_error:
                msg = 'Database does not exists, check name and try again'
            else:
                msg = 'Could not dump database, error message: {0}'.format(str_error)
            logger.error(msg)
            raise errors.DumpError(msg)
        return destiny_file

    def drop(self, database_name, force=False):
        """Drops a database using *dropdb* command.

        :param database_name: Database name to be deleted.
        :type database_name: str
        :returns: If succeeded (True) or not (None).
        :rtype: bool or None
        """
        cnf = self.__config
        if force:
            self.terminate_sessions(database_name, cnf.get("owner"),
                                    cnf.get("owner_password"))
        cnf.update({'dbname': database_name})
        logger.debug('drop: %s', database_name)
        if self.__config.get('password', False):
            os.environ['PGPASSWORD'] = self.__config.get('password')
        dropdb_cmd = 'dropdb {dbname}'
        dropdb_cmd = self.__format_cmd(dropdb_cmd, cnf)
        dropdb_cmd = dropdb_cmd.format(**cnf)
        shell = spur.LocalShell()
        try:
            shell.run(shlex.split(dropdb_cmd))
        except spur.results.RunProcessError as error:
            str_error = utils.decode(error.stderr_output)
            if 'does not exist' in str_error:
                return True
            logger.error('Could not drop database, error message: %s', str_error)
            raise OperationalError(str_error)
        else:
            return True

    def create(self, database_name):
        """Executes a *createdb* command.

        :param database_name: Database name.
        :type database_name: str
        :returns: The created database name.
        :rtype: str
        """
        cnf = self.__config
        cnf.update({'dbname': database_name})
        logger.debug("Creating database %s", database_name)
        if self.__config.get('password', False):
            os.environ['PGPASSWORD'] = self.__config.get('password')
        createdb_cmd = 'createdb \"{dbname}\" -T template0 -E utf8 --lc-collate C'
        createdb_cmd = self.__format_cmd(createdb_cmd, cnf)
        createdb_cmd = createdb_cmd.format(**cnf)
        shell = spur.LocalShell()
        try:
            shell.run(shlex.split(createdb_cmd))
        except spur.results.RunProcessError as error:
            str_error = utils.decode(error.stderr_output)
            logger.error('Could not create database, error message: %s', str_error)
            raise OperationalError(str_error)
        return database_name

    def restore(self, database_name, dump_name, jobs=False):
        """Restores a database dump in sql plain format, tries to create database if it doesn't
        exist.

        :param database_name: Database where the dump will be restored.
        :type database_name: str
        :param dump_name: Full path and name of the sql dump to restore.
        :type dump_name: str
        :returns: If succeeded (True) or not (None).
        :rtype: bool or None
        """
        cnf = self.__config
        cnf.update({'dbname': database_name})

        if self.__config.get('password', False):
            os.environ['PGPASSWORD'] = self.__config.get('password')
        self.__config.update({'dbname': database_name})
        restore_cmd = 'psql {dbname} -f {0}'
        if jobs:
            restore_cmd = 'pg_restore -j {num} -F d {0} -d {dbname} -x'
            cnf.update({'num': str(jobs)})
        restore_cmd = self.__format_cmd(restore_cmd, cnf)
        restore_cmd = restore_cmd.format(dump_name, **cnf)
        shell = spur.LocalShell()
        self.create(database_name)
        try:
            shell.run(shlex.split(restore_cmd))
        except spur.results.RunProcessError as error:
            str_error = utils.decode(error.stderr_output)
            logger.error('Could not restore database, error message: %s', str_error)
            self.drop(database_name)
            raise OperationalError(str_error)
        else:
            res = True
        return res

    def create_extension_unaccent(self, database_name):
        """ Creates the unaccent extension in the specified database

        :param database_name: Name of the database where the extension will be created
        """
        config = self.__config.copy()
        config.update({'dbname': database_name})
        logger.info('Creating extension unaccent in the database %s', database_name)
        try:
            with PostgresConnector(config) as db:
                db.execute("create extension unaccent;")
        except (psycopg2.ProgrammingError, psycopg2.OperationalError) as error:
            error_msg = utils.get_error_message(error)
            allowed_errors = ['permission denied to create extension',
                              'password authentication failed']
            if 'extension "unaccent" already exists' in error_msg:
                logger.info(error_msg.strip())
                return
            elif any(err in error_msg for err in allowed_errors):
                logger.error(
                    'Unable to create the unaccent extension, authentication for the'
                    ' postgres user in the deployv.conf file failed or the'
                    ' user is not superuser'
                )
                return
            raise

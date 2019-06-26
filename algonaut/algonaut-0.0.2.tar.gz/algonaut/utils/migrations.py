import re
import os
import yaml
import logging
import traceback

from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

logger = logging.getLogger(__name__)

class MigrationError(BaseException):
    pass

class MigrationManager(object):

    """
    A migration manager class.
    """

    def __init__(self, path, connection):
        self.path = path
        self.connection = connection
        self.connection.autocommit = True
        self.load_config()
        self.load_migrations()

    def load_config(self):
        """
        Loads the configuration.
        """
        with open(os.path.join(self.path,'config.yml'),'r') as input_file:
            content = input_file.read()
        self.config = yaml.load(content)

    def load_migrations(self, encoding='utf-8'):
        """
        Loads the migrations.
        """
        filenames = os.listdir(self.path)
        self.migrations = defaultdict(dict)
        for filename in filenames:
            match = re.match('^(\d+)_(up|down)_(.*)\.sql$', filename, re.I)
            if match:
                version = int(match.group(1))
                direction = match.group(2)
                description = match.group(3)
                with open(os.path.join(self.path, filename),'r', encoding=encoding) as input_file:
                    content = input_file.read()
                self.migrations[version][direction] = {
                    'version' : int(version),
                    'description' : description,
                    'filename' : filename,
                    'script' : content
                }

    def get_current_version(self):
        """
        Returns the current version of the database schema.
        """
        context = {
            'version_table' : self.config['version_table']['name'],
            'version_column' : self.config['version_table']['version_column'],
        }
        try:
            result = self.connection.execute("SELECT {version_column} FROM {version_table}".format(**context))
        except ProgrammingError:
            logger.warning("It seems the version table does not exist yet...")
            return 0
        version = result.fetchone()
        if version is not None:
            version = int(version[0])
        else:
            version = 0
        return version

    def update_version_table(self, version):
        count_result = self.connection.execute("SELECT COUNT('*') FROM {}"\
                                    .format(self.config['version_table']['name']))
        count = count_result.fetchone()[0]
        context = {
            'version_table' : self.config['version_table']['name'],
            'version_column' : self.config['version_table']['version_column'],
            'version' : version
        }
        if count == 0:
            result = self.connection.execute("INSERT INTO {version_table} ({version_column}) values ({version})".format(**context))
        elif count == 1:
            result = self.connection.execute("UPDATE {version_table} SET {version_column} = {version}".format(**context))
        else:
            raise MigrationError("Version table has more than one entry ({})!".format(count))


    def migrate(self, version=None, in_transaction=True):
        """
        Runs the database migrations.
        """
        current_version = self.get_current_version()
        direction = 'up'
        if version is None:
            migrations = [
                (v,migration.get('up')) for v, migration in self.migrations.items()
                if v > current_version
            ]
        else:
            if version > current_version:
                migrations = [
                    (v,migration.get('up')) for v, migration in self.migrations.items()
                    if v > current_version and v <= version
                ]
            else:
                direction = 'down'
                migrations = [
                    (v,migration.get('down')) for v, migration in self.migrations.items()
                    if v <= current_version and v > version
                ]
        migrations = sorted(migrations, key=lambda x: -x[0] if direction == 'down' else x[0])
        for v, migration in migrations:
            if migration is None:
                raise MigrationError("Migration for version {} and direction '{}' not defined, cannot continue!".format(v, direction))
        if not migrations:
            logger.info("Database is already up-to-date, aborting...")
            return
        if in_transaction:
            with self.connection.begin():
                self.execute_migrations(migrations, direction, in_transaction=False)
        else:
            self.execute_migrations(migrations, direction, in_transaction=True)

    def execute_migrations(self, migrations, direction, in_transaction=True):
        logger.info("Executing migrations {} in direction '{}'"\
                    .format(", ".join(['{}'.format(m[0]) for m in migrations]), direction))
        for v, migration in migrations:
            try:
                logger.info("Executing migration {}...".format(migration['filename']))
                self.connection.execute("SET statement_timeout = 0; SET lock_timeout = 0;")
                if in_transaction:
                    with self.connection.begin():
                        result = self.connection.execute(text(migration['script']))
                else:
                    result = self.connection.execute(text(migration['script']))
            except ProgrammingError as pe:
                logger.error("An error occurred when executing migration {}, aborting...".format(migration['filename']))
                raise MigrationError(str(pe))

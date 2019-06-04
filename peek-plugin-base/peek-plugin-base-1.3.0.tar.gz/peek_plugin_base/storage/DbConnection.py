import logging
from io import StringIO
from textwrap import dedent
from threading import Lock
from typing import Optional, Dict, Union, Callable, Iterable

import sqlalchemy_utils
from peek_plugin_base.storage.AlembicEnvBase import ensureSchemaExists, isMssqlDialect, \
    isPostGreSQLDialect
from pytmpdir.Directory import Directory
from sqlalchemy import create_engine, Integer
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.schema import MetaData, Sequence
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)

DbSessionCreator = Callable[[], Session]

DelcarativeIdGen = Optional[Iterable[int]]
DeclarativeIdCreator = Callable[[object, int], DelcarativeIdGen]


class DbConnection:
    def __init__(self, dbConnectString: str, metadata: MetaData, alembicDir: str,
                 dbEngineArgs: Optional[Dict[str, Union[str, int]]] = None,
                 enableForeignKeys=False, enableCreateAll=True):
        """ SQLAlchemy Database Connection

        This class takes care of migrating the database and establishing thing database
        connections and ORM sessions.

        :param dbConnectString:
            The connection string for the DB.
            See http://docs.sqlalchemy.org/en/latest/core/engines.html

        :param metadata:
            The instance of the metadata for this connection,
            This is schema qualified MetaData(schema="schama_name")

        :param alembicDir:
            The absolute location of the alembic directory (versions dir lives under this)

        :param dbEngineArgs:
            The arguments to pass to the database engine, See
            http://docs.sqlalchemy.org/en/latest/core/engines.html#engine-creation-api

        :param enableCreateAll:
            If the schema doesn't exist, then the migration is allowed
            to use matadata.create_all()

        :param enableForeignKeys:
            Perform a check to ensure foriegn keys have indexes after the db is
            migrated and connected.
        """
        self._dbConnectString = dbConnectString
        self._metadata = metadata
        self._alembicDir = alembicDir

        self._dbEngine = None
        self._ScopedSession = None
        self._dbEngineArgs = dbEngineArgs if dbEngineArgs else {"echo": False}

        self._sequenceMutex = Lock()

        self._enableForeignKeys = enableForeignKeys
        self._enableCreateAll = enableCreateAll

    def closeAllSessions(self):
        """ Close All Session

        Close all ORM sessions connected to this DB engine.

        """
        self.ormSessionCreator()  # Ensure we have a session maker and session
        self._ScopedSession.close_all()

    @property
    def ormSessionCreator(self) -> DbSessionCreator:
        """ Get Orm Session

        :return: A SQLAlchemy session scoped for the callers thread..
        """
        assert self._dbConnectString

        if self._ScopedSession:
            return self._ScopedSession

        self._dbEngine = create_engine(
            self._dbConnectString,
            **self._dbEngineArgs
        )

        self._ScopedSession = scoped_session(
            sessionmaker(bind=self._dbEngine))

        return self._ScopedSession

    @property
    def dbEngine(self) -> Engine:
        """ Get DB Engine

        This is not thread safe, use the ormSesson to execute SQL statements instead.
        self.ormSession.execute(...)

        :return: the DB Engine used to connect to the database.

        """
        return self._dbEngine

    def migrate(self) -> None:
        """ Migrate

        Perform a database migration, upgrading to the latest schema level.
        """

        assert self.ormSessionCreator, "ormSessionCreator is not defined"

        connection = self._dbEngine.connect()
        isDbInitialised = self._dbEngine.dialect.has_table(
            connection, 'alembic_version',
            schema=self._metadata.schema)
        connection.close()

        if isDbInitialised or not self._enableCreateAll:
            self._doMigration(self._dbEngine)

        else:
            self._doCreateAll(self._dbEngine)

        if self._enableForeignKeys:
            self.checkForeignKeys(self._dbEngine)

    def checkForeignKeys(self, engine: Engine) -> None:
        """ Check Foreign Keys

        Log any foreign keys that don't have indexes assigned to them.
        This is a performance issue.

        """
        missing = (sqlalchemy_utils.functions
                   .non_indexed_foreign_keys(self._metadata, engine=engine))

        for table, keys in missing.items():
            for key in keys:
                logger.warning("Missing index on ForeignKey %s" % key.columns)

    @deferToThreadWrapWithLogger(logger)
    def prefetchDeclarativeIds(self, Declarative, count) -> DelcarativeIdGen:
        """ Prefetch Declarative IDs

        This function prefetches a chunk of IDs from a database sequence.
        Doing this allows us to preallocate the IDs before an insert, which significantly
        speeds up :

        * Orm inserts, especially those using inheritance
        * When we need the ID to assign it to a related object that we're also inserting.

        :param Declarative: The SQLAlchemy declarative class.
            (The class that inherits from DeclarativeBase)

        :param count: The number of IDs to prefetch

        :return: An iterable that dispenses the new IDs
        """
        return _commonPrefetchDeclarativeIds(
            self.dbEngine, self._sequenceMutex, Declarative, count
        )

    def _runAlembicCommand(self, command, *args):
        configFile = self._writeAlembicIni()

        from alembic.config import Config
        alembic_cfg = Config(configFile.name)
        command(alembic_cfg, *args)

    def _doCreateAll(self, engine):
        ensureSchemaExists(engine, self._metadata.schema)
        self._metadata.create_all(engine)

        from alembic import command
        self._runAlembicCommand(command.stamp, "head")

    def _writeAlembicIni(self):
        cfg = '''
        [alembic]
        script_location = %(alembicDir)s

        sourceless = true
        sqlalchemy.url = %(url)s

        [alembic:exclude]
        tables = spatial_ref_sys

        [logging]
        default_level = INFO
        '''
        cfg = dedent(cfg)

        cfg %= {'alembicDir': self._alembicDir,
                'url': self._dbConnectString}

        dir = Directory()
        file = dir.createTempFile()

        with file.open(write=True) as f:
            f.write(cfg)

        return file.namedTempFileReader()

    def _doMigration(self, engine):
        ensureSchemaExists(engine, self._metadata.schema)

        from alembic import command
        self._runAlembicCommand(command.upgrade, "head")


def convertToCoreSqlaInsert(ormObj, Declarative):
    insertDict = dict()

    for fieldName in Declarative.tupleFieldNames():
        value = getattr(ormObj, fieldName)

        if value is None:
            Col = getattr(Declarative, fieldName)
            if isinstance(Col, InstrumentedAttribute):
                value = Col.server_default.arg if Col.server_default else None
                if value == 'false':
                    value = False

                elif value == 'true':
                    value = True

        insertDict[fieldName] = value

    return insertDict


def pgCopyInsert(rawConn, table, inserts):
    colTypes = [c.type for c in table.c]

    def convert(index, val):
        if val is None:
            return '\\N'

        if isinstance(colTypes[index], Integer):
            return str(val).split('.')[0]

        return str(val).replace('\\', '\\\\') \
            .replace('\t', '\\t') \
            .replace('\n', '\\n') \
            .replace('\r', '\\r')

    columns = [str(c).split('.')[1] for c in table.c]
    f = StringIO()
    for insert in inserts:
        line = ''
        for i, c in enumerate(columns):
            line += convert(i, insert[c])
            line += '\n' if i == len(columns) - 1 else '\t'

        f.write(line)

    f.seek(0)

    cursor = rawConn.cursor()
    cursor.copy_from(f, '"%s"."%s"' % (table.schema, table.name),
                     sep='\t', null='\\N',
                     columns=tuple(['"%s"' % c for c in columns]))
    f.close()
    cursor.close()


def _commonPrefetchDeclarativeIds(engine, mutex,
                                  Declarative, count) -> Optional[Iterable[int]]:
    """ Common Prefetch Declarative IDs

    This function is used by the worker and server
    """
    if not count:
        logger.debug("Count was zero, no range returned")
        return

    conn = engine.connect()
    transaction = conn.begin()
    mutex.acquire()
    try:
        sequence = Sequence('%s_id_seq' % Declarative.__tablename__,
                            schema=Declarative.metadata.schema)

        if isPostGreSQLDialect(engine):
            sql = "SELECT setval('%(seq)s', (select nextval('%(seq)s') + %(add)s), true)"
            sql %= {
                'seq': '"%s"."%s"' % (sequence.schema, sequence.name),
                'add': count
            }
            nextStartId = conn.execute(sql).fetchone()[0]
            startId = nextStartId - count

        elif isMssqlDialect(engine):
            startId = conn.execute(
                'SELECT NEXT VALUE FOR "%s"."%s"'
                % (sequence.schema, sequence.name)
            ).fetchone()[0] + 1

            nextStartId = startId + count

            conn.execute('alter sequence "%s"."%s" restart with %s'
                         % (sequence.schema, sequence.name, nextStartId))

        else:
            raise NotImplementedError()

        transaction.commit()

        return iter(range(startId, nextStartId))

    finally:
        mutex.release()
        conn.close()

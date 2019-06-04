# @TODO Convert to `pickle` in py3
import cPickle
import os
import sqlite3
import tempfile
import threading

import msgpack
import redis

from .log import Log, Entry
from .state import State, STATE_ROLE_FOLLOWER


class Storage(object):
    """
    An interface to describe how `pyraftlog.state.State` should be retrieved and persisted.
    """

    def retrieve(self, state):
        """
        Retrieve the state of the given name from storage.
        Must always be a `Follower` as we have that is the default.

        :param state: State to have the data retrieved into
        :type state: pyraftlog.state.State
        :return: The loaded state
        :rtype: pyraftlog.state.Follower
        """
        return state or State(STATE_ROLE_FOLLOWER, '')

    def persist(self, state):
        """
        Persist the given state to storage.

        :param state: State to be persisted
        :type state: pyraftlog.state.State
        :return: True if successful
        :rtype: bool
        """
        return True

    def exists(self):
        """
        Checks as to whether there is any data stored.

        :return: True if there is anything stored
        :rtype: bool
        """
        raise NotImplementedError

    def migrate(self, state, from_storage, force=False):
        """
        Migrates the data stored in `from_storage` into `to_storage`.
        This will replace/overwrite the data stored in `to_storage`.

        :param state:
        :param from_storage:
        :param force: Override the existing storage with the migrated
        :type state: pyraftlog.state.State
        :type from_storage: pyraftlog.storage.Storage
        :type force: bool
        :return: True if the data was migrated, False otherwise
        :rtype: bool
        """
        if from_storage.exists() and (force or not self.exists()):
            return self.persist(from_storage.retrieve(state))
        return False


class FileStorage(Storage):
    """
    Abstract base for all FileStorage.
    """

    ext = None  # type: str
    ''' Default extension (added only if `file_path` excludes ext, set to `None` for no ext) '''

    def __init__(self, file_path):
        """
        :param file_path: Path to the file of the state storage
        :type file_path: str
        """
        if self.ext:
            file_path, ext = os.path.splitext(file_path)
            file_path = file_path + (ext or self.ext)
        self.file_path = file_path

    def exists(self):
        return os.path.exists(self.file_path) and os.path.isfile(self.file_path) and os.path.getsize(self.file_path) > 0


class PickleStorage(FileStorage):
    """
    This storage type uses `cPickle` to serialise the state which is then written to disk.
    """

    ext = '.pickle'

    def retrieve(self, state):
        if self.exists():
            with open(self.file_path, 'r') as f:
                state.populate(cPickle.loads(f.read()))

        return state

    def persist(self, state):
        # Atomically write the state to file
        with tempfile.NamedTemporaryFile(dir=os.path.dirname(self.file_path), delete=False) as t:
            t.write(cPickle.dumps(state, 2))
            t.flush()
            # os.fsync(t.fileno())
            os.rename(t.name, self.file_path)


class SQLiteStorage(FileStorage):
    """
    This storage type uses `SQLite` to control read/write of data.
    It is optimised with the assumption that most logs are committed use after being appended.
    """

    ext = '.sqlite'

    def __init__(self, file_path):
        """
        :param file_path: Path to the storage file
        :type file_path: str
        """
        super(SQLiteStorage, self).__init__(file_path)
        self.lock = threading.Lock()
        self._database_connection = None

    def retrieve(self, state):
        if self.exists():
            with self.lock:
                retrieved = {}
                self.__retrieve_metadata_from_storage(retrieved)
                self.__retrieve_logs_from_storage(retrieved)
                state.populate(retrieved)
        return state

    def persist(self, state):
        with self.lock:
            logs = self.__extract_logs_from_state(state)
            metadata = self.__extract_metadata_from_state(state)
            cur = self.database_connection.cursor()
            if state.log_reduction:
                cur.execute('DELETE FROM "logs" WHERE "index" <= ?', (state.log.offset,))
            cur.executemany('INSERT INTO "logs"("index", "term" , "value") VALUES(?, ?, ?)', logs)
            cur.executemany('REPLACE INTO metadata("name", "value") VALUES(?, ?)', metadata)
            self.database_connection.commit()

    @property
    def database_connection(self):
        """
        If no database connection established, this method will establish the connection and initialise the database.

        :return: SQLite database connection
        :rtype: sqlite3.Connection
        """
        if self._database_connection:
            return self._database_connection

        self._database_connection = sqlite3.connect(self.file_path, check_same_thread=False)
        self._database_connection.text_factory = str
        self.__initialise_database()
        return self._database_connection

    def __initialise_database(self):
        """
        Initialises the SQLite database using `CREATE TABLE IF NOT EXISTS`.

        :rtype: None
        """
        cur = self._database_connection.cursor()
        sql_create_logs_table = ''' CREATE TABLE IF NOT EXISTS "logs" (
                                        "index" INTEGER NOT NULL PRIMARY KEY ON CONFLICT IGNORE,
                                        "term" INTEGER NOT NULL,
                                        "value" BLOB NOT NULL
                                    ); '''
        sql_create_metadata_table = ''' CREATE TABLE IF NOT EXISTS "metadata" (
                                            "name" TEXT NOT NULL PRIMARY KEY,
                                            "value" BLOB NOT NULL
                                        ); '''
        cur.execute(sql_create_logs_table)
        cur.execute(sql_create_metadata_table)
        self._database_connection.commit()

    def __extract_logs_from_state(self, state):
        """
        Extract the logs from in memory state in the correct format.

        :param state: State to extract logs from
        :type state: pyraftlog.state.State
        :rtype: list[tuple]
        """
        cur = self.database_connection.cursor()
        cur.execute('SELECT MAX("index") FROM "logs"')
        stored_index = cur.fetchone()[0] or 0
        logs = [(x.idx, x.term, msgpack.dumps(x.value))
                for x
                in state.log.entries[min(stored_index, state.commit_index) - state.log.offset:]]
        return logs

    @staticmethod
    def __extract_metadata_from_state(state):
        """
        Extract metadata in the correct format to store from in memory state.

        :param state: State to extract metadata from
        :type state: pyraftlog.state.State
        :rtype: list[tuple]
        """
        metadata = [('current_term', sqlite3.Binary(msgpack.dumps(state.current_term))),
                    ('commit_index', sqlite3.Binary(msgpack.dumps(state.commit_index))),
                    ('last_applied', sqlite3.Binary(msgpack.dumps(state.last_applied))),
                    ('cluster_applied', sqlite3.Binary(msgpack.dumps(state.cluster_applied))),
                    ('voted_for', sqlite3.Binary(msgpack.dumps(state.cluster_applied))),
                    ('log_reduction', sqlite3.Binary(msgpack.dumps(state.log_reduction)))]
        return metadata

    def __retrieve_metadata_from_storage(self, data):
        """
        Retrieves metadata from the SQLite database.

        :param data: Container to hold retrieved metadata
        :type data: dict
        :rtype: None
        """
        cur = self.database_connection.cursor()
        cur.execute('SELECT * FROM "metadata"')
        rows = cur.fetchall()
        for row in rows:
            data[str(row[0])] = msgpack.loads(str(row[1]))

    def __retrieve_logs_from_storage(self, data):
        """
        Retrieves logs from SQLite database.

        :param data: Container to hold retrieved logs
        :type data: dict
        :rtype: None
        """
        cur = self.database_connection.cursor()
        cur.execute('SELECT "term", "index", "value" FROM "logs"')
        rows = cur.fetchall()
        logs = [Entry(x[0], x[1], msgpack.loads(str(x[2]))) for x in rows]
        data['log'] = Log(logs)


class RedisStorage(Storage):
    """
    This storage type uses Redis
    """

    def __init__(self, redis_client, key_prefix='raft_'):
        """
        :param redis_client: Instantiated redis client
        :param key_prefix:
        :type redis_client: redis.Redis
        :type key_prefix: str
        """
        self.redis_client = redis_client
        self.key_prefix = key_prefix

    def retrieve(self, state):
        # Retrieve the data from redis
        value = self.redis_client.get(self.key_prefix + 'state')
        if value:
            value = cPickle.loads(value)
            state.populate(value)

        return state

    def persist(self, state):
        self.redis_client.set(self.key_prefix + 'state', cPickle.dumps(state, 2))

    def exists(self):
        return self.redis_client.get(self.key_prefix + 'state')

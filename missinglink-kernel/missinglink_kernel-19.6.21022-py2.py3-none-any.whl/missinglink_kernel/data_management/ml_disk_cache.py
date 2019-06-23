# -*- coding: utf-8 -*-

import logging
import threading
import os
import errno
import tempfile
import sqlite3
import time
from collections import namedtuple

from .diskcache import Cache, Disk
from .diskcache.core import DEFAULT_SETTINGS, METADATA, EVICTION_POLICY, DBNAME


class _CacheDB(Cache):
    BULK_UPDATE_SIZE = int(os.environ.get('_ML_BULK_UPDATE_SIZE', 100))

    # pylint: disable=bad-continuation
    # noinspection PyMissingConstructor
    def __init__(self, directory, timeout=60, disk=Disk, bulk_size=BULK_UPDATE_SIZE, **custom_settings):
        """Initialize cache instance.

        :param str directory: cache directory
        :param float timeout: SQLite connection timeout
        :param disk: Disk type or subclass for serialization
        :param bool perform_db_init: whether to perform the SQLite initialization
        :param custom_settings: any of DEFAULT_SETTINGS

        """
        try:
            assert issubclass(disk, Disk)
        except (TypeError, AssertionError):
            raise ValueError('disk must subclass diskcache.Disk')

        self._directory = directory
        self._timeout = 1
        self._local = threading.local()
        self._txn_id = None
        self._bulk_size = bulk_size

        self.assure_folder(directory)

        # Close and re-open database connection with given timeout.

        self._timeout = timeout

        self._pending_updates = []
        self._last_update = time.time()

        self._pending_accessed_files = []

    def _get_db_settings(self, settings):
        sets = DEFAULT_SETTINGS.copy()
        sets['cull_limit'] = self._bulk_size  # needed in order to make sure the eviction works correctly
        sets.update(settings)

        for key in METADATA:
            sets.pop(key, None)

        return sets

    def _init_disk(self, disk, directory, sets):
        kwargs = {
            key[5:]: value for key, value in sets.items()
            if key.startswith('disk_')
        }
        self._disk = disk(directory, **kwargs)

    @staticmethod
    def assure_folder(directory):
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory, 0o755)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    raise EnvironmentError(
                        error.errno,
                        'Cache directory "%s" does not exist'
                        ' and could not be created' % directory
                    )

    def _set_page_size(self):
        (self._page_size,), = self._sql_retry('PRAGMA page_size').fetchall()


# noinspection SqlResolve
class _CreateCacheDB(_CacheDB):
    def _set_cached_attributes(self, sets):
        sql = self._sql_retry

        for key, value in sets.items():
            query = 'INSERT OR REPLACE INTO Settings VALUES (?, ?)'
            sql(query, (key, value))
            self.reset(key, value)

        for key, value in METADATA.items():
            query = 'INSERT OR IGNORE INTO Settings VALUES (?, ?)'
            sql(query, (key, value))
            self.reset(key)

        self._set_page_size()

    def _setup_cache_table(self):
        sql = self._sql_retry

        sql('CREATE TABLE IF NOT EXISTS Cache ('
            ' rowid INTEGER PRIMARY KEY,'
            ' key BLOB,'
            ' raw INTEGER,'
            ' store_time REAL,'
            ' expire_time REAL,'
            ' access_time REAL,'
            ' access_count INTEGER DEFAULT 0,'
            ' tag BLOB,'
            ' size INTEGER DEFAULT 0,'
            ' mode INTEGER DEFAULT 0,'
            ' filename TEXT,'
            ' value BLOB)')

        sql('CREATE UNIQUE INDEX IF NOT EXISTS Cache_key_raw ON'
            ' Cache(key, raw)')

        sql('CREATE INDEX IF NOT EXISTS Cache_expire_time ON'
            ' Cache (expire_time)')

        # noinspection PyUnresolvedReferences
        query = EVICTION_POLICY[self.eviction_policy]['init']

        if query is not None:
            sql(query)

    def _cleanup_temp_dir(self):
        try:
            os.rmdir(self._directory)
        except IOError:
            logging.debug('Failed cleaning up temp cache directory')
            pass

    def _set_sqlite_settings(self, sets):
        for key, value in sorted(sets.items()):
            if key.startswith('sqlite_'):
                self.reset(key, value, update=False)

    def _create_settings_table(self):
        sql = self._sql_retry

        sql('CREATE TABLE IF NOT EXISTS Settings ('
            ' key TEXT NOT NULL UNIQUE,'
            ' value)')

    def _move_db_files_to_directory(self, target_directory):
        for current_dir_path, __, file_names in os.walk(self._directory):
            for file_name in file_names:
                source_file_path = os.path.join(current_dir_path, file_name)
                target_file_path = os.path.join(target_directory, file_name)
                os.rename(source_file_path, target_file_path)

    def initialize_db(self, directory, sets, disk):
        logging.debug('Initializing disk cache')
        self.assure_folder(self._directory)
        self._db_init(directory, sets, disk)
        self.close()
        self._move_db_files_to_directory(directory)
        self._cleanup_temp_dir()
        self._directory = directory

    def _db_init(self, directory, sets, disk):
        # Chance to set pragmas before any tables are created.

        self._set_sqlite_settings(sets)
        self._create_settings_table()

        # Setup Disk object (must happen after settings initialized).

        self._init_disk(disk, directory, sets)

        # Set cached attributes: updates settings and sets pragmas.

        self._set_cached_attributes(sets)

        self._setup_cache_table()

        self._create_metadata_triggers()

        self._process_index_tag()

    def _create_metadata_triggers(self):
        sql = self._sql_retry

        sql('CREATE TRIGGER IF NOT EXISTS Settings_count_insert'
            ' AFTER INSERT ON Cache FOR EACH ROW BEGIN'
            ' UPDATE Settings SET value = value + 1'
            ' WHERE key = "count"; END')

        sql('CREATE TRIGGER IF NOT EXISTS Settings_count_delete'
            ' AFTER DELETE ON Cache FOR EACH ROW BEGIN'
            ' UPDATE Settings SET value = value - 1'
            ' WHERE key = "count"; END')

        sql('CREATE TRIGGER IF NOT EXISTS Settings_size_insert'
            ' AFTER INSERT ON Cache FOR EACH ROW BEGIN'
            ' UPDATE Settings SET value = value + NEW.size'
            ' WHERE key = "size"; END')

        sql('CREATE TRIGGER IF NOT EXISTS Settings_size_update'
            ' AFTER UPDATE ON Cache FOR EACH ROW BEGIN'
            ' UPDATE Settings'
            ' SET value = value + NEW.size - OLD.size'
            ' WHERE key = "size"; END')

        sql('CREATE TRIGGER IF NOT EXISTS Settings_size_delete'
            ' AFTER DELETE ON Cache FOR EACH ROW BEGIN'
            ' UPDATE Settings SET value = value - OLD.size'
            ' WHERE key = "size"; END')

    def _process_index_tag(self):
        # Create tag index if requested.

        # noinspection PyUnresolvedReferences
        if self.tag_index:
            self.create_tag_index()
        else:
            self.drop_tag_index()


# noinspection SqlResolve
class MLDiskCache(_CacheDB):
    """
    Disk and file backed cache.
    This class is different from the original diskcache.Cache in the following ways:
    1. It separates the DB initialization from the class init, allowing the DB init to be done only once
    2. Increases the timeout from 0 to 1 sec during init.
    3. Update SQLite + delete files if necessary on batches (according to BULK_UPDATE_SIZE), instead of on all updates
    """

    MAX_UPDATE_INTERVAL_SECONDS = int(os.environ.get('_ML_MAX_UPDATE_INTERVAL_SECONDS', 60))
    ACCESSED_FILES_BULK_SIZE = int(os.environ.get('_ML_ACCESSED_FILES_BULK_SIZE', 1000))

    # pylint: disable=bad-continuation
    # noinspection PyMissingConstructor
    def __init__(self, directory, timeout=60, disk=Disk, bulk_size=_CacheDB.BULK_UPDATE_SIZE, **custom_settings):
        """Initialize cache instance.

        :param str directory: cache directory
        :param float timeout: SQLite connection timeout
        :param disk: Disk type or subclass for serialization
        :param bool perform_db_init: whether to perform the SQLite initialization
        :param custom_settings: any of DEFAULT_SETTINGS

        """
        super(MLDiskCache, self).__init__(directory, timeout, disk, bulk_size, **custom_settings)

        perform_db_init = self.__was_db_initialized(directory)

        if perform_db_init:
            tmp_directory = tempfile.mkdtemp(dir=directory)
            create_db = _CreateCacheDB(tmp_directory, timeout, disk, bulk_size, **custom_settings)
            all_settings = self._get_db_settings(custom_settings)

            create_db.initialize_db(directory, all_settings, disk)

        all_settings = self._get_db_settings(custom_settings)
        self._use_existing_db(directory, all_settings, disk, custom_settings)

        # Close and re-open database connection with given timeout.
        self.close()
        # noinspection PyStatementEffect
        self._sql  # pylint: disable=pointless-statement

    def _use_existing_db(self, directory, sets, disk, custom_settings):
        logging.debug('Using existing disk cache')
        self._update_sets_with_current_settings(sets)
        self._init_disk(disk, directory, sets)
        self._init_properties(sets, custom_settings)

    @staticmethod
    def __was_db_initialized(directory):
        db_path = MLDiskCache._get_expected_db_path(directory)
        return not os.path.isfile(db_path)

    def _update_sets_with_current_settings(self, sets):
        sql = self._sql_retry
        try:
            current_settings = dict(sql(
                'SELECT key, value FROM Settings'
            ).fetchall())
        except sqlite3.OperationalError:
            current_settings = {}

        sets.update(current_settings)

    @staticmethod
    def _get_expected_db_path(directory):
        return os.path.join(directory, DBNAME)

    def _init_properties(self, all_settings, custom_settings):
        for key, value in all_settings.items():
            if key.startswith('disk_'):
                attr = key[5:]
                setattr(self._disk, attr, value)
            else:
                setattr(self, key, value)

        for key, value in custom_settings.items():
            self.reset(key, value)

        self._set_page_size()

    ROW = namedtuple('ROW', [
        'db_key',
        'raw',
        'now',
        'expire_time',
        'tag',
        'size',
        'mode',
        'filename',
        'db_value',
    ])

    def set(self, key, value, expire=None, read=False, tag=None, retry=False):
        """Set `key` and `value` item in cache.

        When `read` is `True`, `value` should be a file-like object opened
        for reading in binary mode.

        :param key: key for item
        :param value: value for item
        :param float expire: seconds until item expires
            (default None, no expiry)
        :param bool read: read value as bytes from file (default False)
        :param str tag: text to associate with key (default None)
        :return: True if item was set
        :raises Timeout: if database timeout expires

        """
        now = time.time()
        db_key, raw = self._disk.put(key)
        expire_time = None if expire is None else now + expire
        size, mode, filename, db_value = self._disk.store(value, read, key=key)

        row = self.ROW(db_key=db_key, raw=raw, now=now, expire_time=expire_time, tag=tag, size=size, mode=mode,
                       filename=filename, db_value=db_value)
        self._pending_updates.append(row)

        if self._should_perform_db_sync(now):
            self._sync_db(now)

    __setitem__ = set

    def _should_perform_db_sync(self, now):
        def pending_updates_over_limit():
            return len(self._pending_updates) >= self._bulk_size

        def update_interval_over_limit():
            return now - self._last_update > self.MAX_UPDATE_INTERVAL_SECONDS

        return pending_updates_over_limit() or update_interval_over_limit()

    def _sync_db(self, now):
        try:
            self._update_transaction(now)
        except sqlite3.OperationalError as ex:
            logging.debug('Got exception while updating cache SQLite: %s', str(ex))
        else:
            self._pending_updates = []
            self._last_update = now

    def _update_transaction(self, now):
        with self._transact() as (sql, cleanup):
            self._batch_update_pending_rows(sql)
            self._update_accessed_files(force=True)
            self._cull(now, sql, cleanup)

    def _batch_update_pending_rows(self, sql):
        for row in self._pending_updates:
            row_values = (
                row.db_key,
                row.raw,
                row.now,  # store_time
                row.expire_time,
                row.now,  # access_time
                0,  # access_count
                row.tag,
                row.size,
                row.mode,
                row.filename,
                row.db_value,
            )
            sql('REPLACE INTO Cache('
                ' key, raw, store_time, expire_time, access_time,'
                ' access_count, tag, size, mode, filename, value'
                ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                row_values
                )

    def mark_path_accessed_time(self, file_path):
        self._pending_accessed_files.append(file_path)
        self._update_accessed_files()

    def _update_accessed_files(self, force=False):
        if not self.__has_pending_accessed_files():
            return

        if not force and not self.__pending_accessed_files_over_limit():
            return

        self.__update_accessed_files()

    def __has_pending_accessed_files(self):
        return len(self._pending_accessed_files) > 0

    def __pending_accessed_files_over_limit(self):
        return len(self._pending_accessed_files) >= self.ACCESSED_FILES_BULK_SIZE

    def __update_accessed_files(self):
        try:
            self._update_accessed_files_transaction()
        except sqlite3.OperationalError as ex:
            logging.debug('Got exception while updating cache SQLite: %s', str(ex))
        else:
            self._pending_accessed_files = []

    def _update_accessed_files_transaction(self):
        def get_update_statement():
            placeholders = ','.join(['?'] * len(self._pending_accessed_files))
            return 'UPDATE Cache SET access_time = ? WHERE filename IN ({})'.format(placeholders)

        def execute_statement(_sql, _statement, *args):
            _sql(_statement, args)

        with self._transact() as (sql, _):
            statement = get_update_statement()
            execute_statement(sql, statement, time.time(), *self._pending_accessed_files)

import os
import sqlite3
from json import dumps, loads
from threading import get_ident
from time import sleep

from esgf_scraper.utils import get_database_info

queue_names = [
    "download_queue",
    "failed_download_queue",
    "postprocess_queue",
    "failed_postprocess_queue",
]


class SqliteQueue(object):
    _create = (
        "CREATE TABLE IF NOT EXISTS {} "
        "("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  item BLOB"
        ")"
    )
    _count = "SELECT COUNT(*) FROM {}"
    _iterate = "SELECT id, item FROM {}"
    _append = "INSERT INTO {} (item) VALUES (?)"
    _write_lock = "BEGIN IMMEDIATE"
    _popleft_get = "SELECT id, item FROM {} " "ORDER BY id LIMIT 1"
    _popleft_del = "DELETE FROM {} WHERE id = ?"
    _peek = "SELECT item FROM {} " "ORDER BY id LIMIT 1"
    _delete_item = "DELETE FROM {} WHERE item = ?"

    def __init__(self, path, table_name="queue"):
        self.path = os.path.abspath(path)
        self.table_name = table_name
        self._connection_cache = {}
        with self._get_conn() as conn:
            conn.execute(self._get_shard(self._create))

    def __len__(self):
        with self._get_conn() as conn:
            return conn.execute(self._get_shard(self._count)).fetchone()[0]

    def __iter__(self):
        with self._get_conn() as conn:
            for id, obj_buffer in conn.execute(self._get_shard(self._iterate)):
                yield loads(str(obj_buffer))

    def _get_shard(self, shard):
        return shard.format(self.table_name)

    def _get_conn(self):
        id = get_ident()
        if id not in self._connection_cache:
            self._connection_cache[id] = sqlite3.Connection(self.path, timeout=60)
        return self._connection_cache[id]

    def append(self, obj, deduplicate=False):
        """
        Appends an item to the queue

        Parameters
        ----------
        obj: dict
            The item to be inserted. Should be able to be converted to a JSON string using dumps.
        deduplicate : bool
            If True, removes any identical items before inserting to ensure that only a single item exists in the queue.

        """
        obj_buffer = dumps(obj)
        with self._get_conn() as conn:
            conn.execute(self._get_shard(self._write_lock))
            if deduplicate:
                conn.execute(self._get_shard(self._delete_item), (obj_buffer,))
            conn.execute(self._get_shard(self._append), (obj_buffer,))
            conn.commit()

    def popleft(self, sleep_wait=True):
        keep_pooling = True
        wait = 0.1
        max_wait = 2
        tries = 0
        with self._get_conn() as conn:
            id = None
            while keep_pooling:
                conn.execute(self._get_shard(self._write_lock))
                cursor = conn.execute(self._get_shard(self._popleft_get))
                try:
                    id, obj_buffer = cursor.fetchone()
                    keep_pooling = False
                except StopIteration:
                    conn.commit()  # unlock the database
                    if not sleep_wait:
                        keep_pooling = False
                        continue
                    tries += 1
                    sleep(wait)
                    wait = min(max_wait, tries / 10 + wait)
            if id:
                conn.execute(self._get_shard(self._popleft_del), (id,))
                return loads(str(obj_buffer))
        return None

    def peek(self):
        with self._get_conn() as conn:
            cursor = conn.execute(self._get_shard(self._peek))
            try:
                return loads(str(cursor.fetchone()[0]))
            except StopIteration:
                return None


def get_queue(table_name):
    assert table_name in queue_names
    return SqliteQueue(get_database_info()["name"], table_name=table_name)

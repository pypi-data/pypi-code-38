import logging
import psycopg2
import psycopg2.extras
import sqlite3

from typing import Any, Dict, Generator, List, Optional

log = logging.getLogger(__name__)


def log_debug(message: str):
    log.debug(message)


class PGDatabase:
    def __init__(self, dsn):
        self.cnx = psycopg2.connect(dsn, cursor_factory=psycopg2.extras.DictCursor)
        self.cnx.autocommit = True
        psycopg2.extras.register_uuid()

    def q(self, sql: str, params: Dict = None) -> List[Dict]:
        """Execute a query and return all rows"""
        if params is None:
            params = {}
        with self.cnx.cursor() as c:
            log_debug(c.mogrify(sql, params).decode())
            c.execute(sql, params)
            return c.fetchall()

    def q_one(self, sql: str, params: Dict = None) -> Optional[Dict]:
        """Execute a query and return the first row, or None if there are no rows"""
        for r in self.q(sql, params):
            return r
        return None

    def q_val(self, sql: str, params: Dict = None) -> Any:
        """Execute a query and return the value in the first column of the first row, or None if there are no rows"""
        for r in self.q(sql, params):
            return r[0]
        return None

    def u(self, sql: str, params: Dict = None) -> int:
        """Execute a statement and return the number of rows affected"""
        if params is None:
            params = {}
        with self.cnx.cursor() as c:
            log_debug(c.mogrify(sql, params).decode())
            c.execute(sql, params)
            return c.rowcount


class SQLiteDatabase:
    def __init__(self, dsn):
        self.cnx = sqlite3.connect(dsn, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cnx.isolation_level = None
        self.cnx.row_factory = sqlite3.Row
        self.cnx.set_trace_callback(log_debug)

    def _q_gen(self, sql: str, params: Dict = None) -> Generator[Dict, None, None]:
        if params is None:
            params = {}
        yield from self.cnx.execute(sql, params)

    def q(self, sql: str, params: Dict = None) -> List[Dict]:
        return list(self._q_gen(sql, params))

    def q_one(self, sql: str, params: Dict = None) -> Optional[Dict]:
        for r in self._q_gen(sql, params):
            return r
        return None

    def q_val(self, sql: str, params: Dict = None) -> Any:
        for r in self._q_gen(sql, params):
            return r[0]
        return None

    def u(self, sql: str, params: Dict = None) -> int:
        if params is None:
            params = {}
        c = self.cnx.execute(sql, params)
        return c.rowcount

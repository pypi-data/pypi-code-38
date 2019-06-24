import logging
import pathlib
import psycopg2
import psycopg2.extras

from typing import Dict, List, Optional

log = logging.getLogger(__name__)


class PGDatabase:
    def __init__(self, dsn):
        self.cnx = psycopg2.connect(dsn, cursor_factory=psycopg2.extras.RealDictCursor)
        self.cnx.autocommit = True

    def q(self, sql: str, params: Dict = None) -> List[Dict]:
        """Execute a query and return all rows"""
        if params is None:
            params = {}
        with self.cnx.cursor() as c:
            log.debug(c.mogrify(sql, params).decode())
            c.execute(sql, params)
            return c.fetchall()

    def q_one(self, sql: str, params: Dict = None) -> Optional[Dict]:
        """Execute a query and return the first row, or None if there are no rows"""
        for r in self.q(sql, params):
            return r
        return None

    def u(self, sql: str, params: Dict = None) -> int:
        """Execute a statement and return the number of rows affected"""
        if params is None:
            params = {}
        with self.cnx.cursor() as c:
            log.debug(c.mogrify(sql, params).decode())
            c.execute(sql, params)
            return c.rowcount

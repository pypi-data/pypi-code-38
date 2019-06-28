import decimal
import logging
import sqlite3
import uuid

from typing import Any, Dict, Generator, List, Optional


def register_adapters_and_converters():
    def convert_bool(value: bytes) -> bool:
        return value == b'True'

    sqlite3.register_adapter(bool, str)
    sqlite3.register_converter('bool', convert_bool)

    def convert_decimal(value: bytes) -> decimal.Decimal:
        return decimal.Decimal(value.decode())

    sqlite3.register_adapter(decimal.Decimal, str)
    sqlite3.register_converter('decimal', convert_decimal)

    def convert_uuid(value: bytes) -> uuid.UUID:
        return uuid.UUID(value.decode())

    sqlite3.register_adapter(uuid.UUID, str)
    sqlite3.register_converter('uuid', convert_uuid)


register_adapters_and_converters()


class SQLiteDatabase:
    def __init__(self, dsn):
        self.log = logging.getLogger(__name__)
        self.cnx = sqlite3.connect(dsn, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cnx.isolation_level = None
        self.cnx.row_factory = sqlite3.Row
        self.cnx.set_trace_callback(self.log.debug)

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

# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

import pandas as pd

from suanpan import utils
from suanpan.log import logger


class RelationalDataWarehouse(object):
    MAX_SQL_LENGTH = 120
    DEFAULT_DB_NAME = "None"
    DTYPE_SQLTYPE_MAPPING = {
        "int8": "tinyint",
        "int16": "smallint",
        "int32": "int",
        "int64": "bigint",
        "float32": "float",
        "float64": "double",
        "class": "text",
        "datetime": "timestamp",
    }

    def __init__(
        self,
        host,
        port,
        user,
        password,
        database,
        **kwargs  # pylint: disable=unused-argument
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    @contextmanager
    def connect(self):
        pass

    def testConnection(self, connection):
        with connection.cursor() as cursor:
            self.selectCurrentTimestamp(cursor)
        logger.info("Database connected")

    def readTable(self, table, partition=None, database=None):
        database = self.database if not database else database
        sql = u"select * from {}.{}".format(database, table)

        if partition and partition.strip():
            conditions = u" and ".join(x.strip() for x in partition.split(","))
            sql = u"{} where {}".format(sql, conditions)

        with self.connect() as connection:
            data = pd.read_sql(sql, connection)
        data = data.rename(index=str, columns=lambda x: x.split(".")[-1])

        return data

    def writeTable(self, table, data, database=None, overwrite=True):
        database = database if database else self.database
        columns = self.getColumns(data)
        with self.connect() as connection:
            try:
                cursor = connection.cursor()
                self.useDatabase(cursor, database)
                if overwrite:
                    self.dropTable(cursor, table)
                self.createTable(cursor, table, columns)
                self.insertData(connection, cursor, table, data)
            finally:
                cursor.close()

    def execute(self, sql):
        with self.connect() as connection:
            with connection.cursor() as cursor:
                return self._execute(cursor, sql)

    def createTable(self, cursor, table, columns):
        self._execute(
            cursor,
            u"create table if not exists {table} ({columns})".format(
                table=table,
                columns=u", ".join(
                    [u"{} {}".format(c["name"], c["type"]) for c in columns]
                ),
            ),
        )

    def dropTable(self, cursor, table):
        self._execute(cursor, u"drop table if exists {}".format(table))

    def insertData(self, connection, cursor, table, data, per=10000):
        dataLength = len(data)
        logger.info(u"Insert into tabel {}: total {}".format(table, dataLength))
        pieces = dataLength // per + 1
        for i in range(pieces):
            begin = per * i
            end = per * (i + 1)
            values = data[begin:end]
            self.insertPiece(connection, cursor, table, values, begin=begin)

    def insertPiece(self, connection, cursor, table, data, begin=0):
        if not data.empty:
            end = begin + len(data)
            logger.info(u"[{} - {}] inserting...".format(begin, end))
            valueGroup = lambda d: u"({})".format(
                u", ".join([u'"{}"'.format(i) for i in d])
            )

            self._execute(
                cursor,
                u"insert into {table} values {values}".format(
                    table=table,
                    values=u", ".join(data.apply(valueGroup, axis=1).values),
                ),
            )
            connection.commit()
            logger.info(u"[{} - {}] Done.".format(begin, end))

    def useDatabase(self, cursor, database):
        self._execute(cursor, u"use {}".format(database))

    def selectCurrentTimestamp(self, cursor):
        self._execute(cursor, u"select current_timestamp")

    def getColumns(self, data):
        return [
            {"name": name.split(".")[-1], "type": self.toSqlType(dtype)}
            for name, dtype in data.dtypes.items()
        ]

    def toSqlType(self, dtype):
        typeName = self.shortenDatetimeType(dtype.name)
        return self.DTYPE_SQLTYPE_MAPPING.get(typeName, "text")

    def shortenDatetimeType(self, typeName):
        datatimeType = "datetime"
        return datatimeType if typeName.startswith(datatimeType) else typeName

    def _execute(self, cursor, sql):
        try:
            return cursor.execute(sql)
        except Exception as e:
            logger.error(utils.shorten("SQL: {}".format(sql), self.MAX_SQL_LENGTH))
            raise e

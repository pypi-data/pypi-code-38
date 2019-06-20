# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

import psycopg2

from suanpan.dw.rdbms import RelationalDataWarehouse


class PostgresDataWarehouse(RelationalDataWarehouse):
    @contextmanager
    def connect(self):
        connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

        yield connection
        connection.close()

# coding=utf-8
from __future__ import absolute_import, print_function

from contextlib import contextmanager

from mysql import connector

from suanpan.dw.rdbms import RelationalDataWarehouse


class MysqlDataWarehouse(RelationalDataWarehouse):
    @contextmanager
    def connect(self):
        connection = connector.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )

        yield connection
        connection.close()

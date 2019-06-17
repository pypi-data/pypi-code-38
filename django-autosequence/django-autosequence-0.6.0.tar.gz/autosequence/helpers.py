from contextlib import contextmanager
from typing import Type

from django.db import connection, transaction, models
from psycopg2.sql import Identifier, SQL

__all__ = ['lock_table']


@contextmanager
def lock_table(model: Type[models.Model]):
    """Locks the table in SHARE ROW EXCLUSIVE MODE

    :param model:  The model whose table you want to lock.
    """
    with transaction.atomic():
        try:
            with connection.cursor() as cursor:
                sql = SQL('LOCK TABLE {tbl} IN SHARE ROW EXCLUSIVE MODE') \
                    .format(
                    tbl=Identifier(model._meta.db_table),
                )
                cursor.execute(sql)
                yield
        finally:
            pass

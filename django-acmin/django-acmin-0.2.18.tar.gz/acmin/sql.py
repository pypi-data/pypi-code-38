import logging
import threading

from django.conf import settings
from django.db.backends.utils import CursorWrapper
from django.db.models.sql.compiler import SQLInsertCompiler, SQLUpdateCompiler, SQLDeleteCompiler
from django.utils.six import wraps

from acmin.utils import attr

logger = logging.getLogger(__name__)


def patch():
    if attr(settings, 'ACMIN_SHOW_SQL'):
        def unset_raw_connection(original):
            def inner(compiler, *args, **kwargs):
                compiler.connection.raw = False
                try:
                    return original(compiler, *args, **kwargs)
                finally:
                    compiler.connection.raw = True

            return inner

        def patch_cursor(original):
            @wraps(original)
            def inner(cursor, sql, *args, **kwargs):
                try:
                    result = original(cursor, sql, *args, **kwargs)
                    return result
                finally:
                    logger.info(f"{threading.currentThread().ident} {sql},{args}")
                    pass

            return inner

        def patch_compiler(original):
            @wraps(original)
            @unset_raw_connection
            def inner(compiler, *args, **kwargs):
                try:
                    return original(compiler, *args, **kwargs)
                finally:
                    s = compiler.as_sql()
                    if type(s) is list and len(s) > 0:
                        s = s[0]
                    sql, params = s
                    logger.info(f"{threading.currentThread().ident} {sql}, {params}")

            return inner

        CursorWrapper.execute = patch_cursor(CursorWrapper.execute)
        CursorWrapper.executemany = patch_cursor(CursorWrapper.executemany)

        for c in (SQLInsertCompiler, SQLUpdateCompiler, SQLDeleteCompiler):  # SQLCompiler
            c.execute_sql = patch_compiler(c.execute_sql)

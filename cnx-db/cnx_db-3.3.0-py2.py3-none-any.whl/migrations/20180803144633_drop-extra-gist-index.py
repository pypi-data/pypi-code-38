# -*- coding: utf-8 -*-
from dbmigrator import deferred


def should_run(cursor):
    cursor.execute("select True from pg_catalog.pg_class where relname = 'modules_moduleid_idx_idx'")
    res = cursor.fetchone()
    return res


def helper(cursor, create_idx, drop_idx, table_name, method, create):
    excpt = None
    # Try creating or drop an index concurrently for at most three times
    tries = 3
    while tries > 0:
        tries -= 1
        try:
            if create:
                # Try creating a new index concurrently
                cursor.execute("CREATE INDEX CONCURRENTLY {} ON {} USING {}"
                               .format(create_idx, table_name, method))
            else:
                # Try dropping the old index concurrently
                cursor.execute("DROP INDEX CONCURRENTLY IF EXISTS {}".format(drop_idx))

        except Exception as e:
            excpt = e
            if create:
                # Drop the incomplete new index if it fails to be created
                cursor.execute("DROP INDEX IF EXISTS {}".format(create_idx))
            continue
        break
    else:
        raise excpt


@deferred
def up(cursor):
    cursor.connection.rollback()
    cursor.connection.autocommit = True
    # Drop the GIST index
    helper(cursor, None, 'modulefti_module_idx_idx', None, None, False)


def down(cursor):
    return

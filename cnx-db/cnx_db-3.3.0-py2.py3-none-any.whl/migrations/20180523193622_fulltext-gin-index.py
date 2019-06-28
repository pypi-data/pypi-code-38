# -*- coding: utf-8 -*-
from dbmigrator import deferred


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
    # Create the GIN index
    helper(cursor, "new_fti_idx", None, "modulefti", "gin(module_idx)", True)
    # Drop the GIST index
    helper(cursor, None, 'fti_idx', None, None, False)
    # Change back the name of the index
    cursor.execute("ALTER INDEX IF EXISTS new_fti_idx RENAME TO fti_idx")
    # Create the GIN index
    helper(cursor, "new_collated_fti_idx", None, "collated_fti", "gin(module_idx)", True)
    # Drop the GIST index
    helper(cursor, None, "collated_fti_idx", None, None, False)
    # Change back the name of the index
    cursor.execute("ALTER INDEX IF EXISTS new_collated_fti_idx RENAME TO collated_fti_idx")


def down(cursor):
    cursor.connection.rollback()
    cursor.connection.autocommit = True
    # Create the GIST index
    helper(cursor, "new_fti_idx", None, "modulefti", "gist(module_idx)", True)
    # Drop the GIN index
    helper(cursor, None, "fti_idx", None, None, False)
    # Change back the name of the index
    cursor.execute("ALTER INDEX IF EXISTS new_fti_idx RENAME TO fti_idx")
    # Create the GIST index
    helper(cursor, "new_collated_fti_idx", None, "collated_fti", "gist(module_idx)", True)
    # Drop the GIN index
    helper(cursor, None, "collated_fti_idx", None, None, False)
    # Change back the name of the index
    cursor.execute("ALTER INDEX IF EXISTS new_collated_fti_idx RENAME TO collated_fti_idx")




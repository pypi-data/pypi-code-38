import logging
import re

logger = logging.getLogger(__name__)

migration_tests = (
    {
        "code": "NOT_NULL",
        "fn": lambda sql, **kw: re.search("NOT NULL", sql)
                                and not re.search("CREATE TABLE", sql),
        "err_msg":
            """When adding new Django fields, make sure to add null=True to the field definition.
            new_field_name = models.CharField(null=True) 
            All new fields must be null by default.
            """,
    },
    {
        "code": "DROP_COLUMN",
        "fn": lambda sql, **kw: re.search("DROP COLUMN", sql),
        "err_msg":
            """A field has been removed from a model. Make sure the field is deprecated (removed from code).
            You can only drop a field after the deprecation process has been deployed. If it's already been deployed,
            you can override this warning.
            """,
    },
    {
        "code": "RENAME_COLUMN",
        "fn": lambda sql, **kw: re.search("ALTER TABLE .* CHANGE", sql)
                                or re.search("ALTER TABLE .* RENAME COLUMN", sql),
        "err_msg":

            """A field has been renamed on a model. You can't rename a field. You must create a new field,
            migrate the data and then remove the old. See documentation for more info.
            """,
    },
    {
        "code": "RENAME_TABLE",
        "fn": lambda sql, **kw: re.search("RENAME TABLE", sql)
                                or re.search("ALTER TABLE .* RENAME TO", sql),
        "err_msg":
            """A model table name has been changed. You should not rename tables. Create a table with the
            new name and migrate the data to the new table.
            """,
    },
    {
        "code": "DROP_TABLE",
        "fn": lambda sql, **kw: re.search("DROP TABLE", sql),
        "err_msg":
            """A model has been removed and a table is being dropped. You must deprecate a model before deleting
            the model. After the deprecation has been deployed you can remove the model. If this has already been done,
            you can override this warning.
            """,
    },
    {
        "code": "CREATE_INDEX_SYNC",
        "fn": lambda sql, **kw: re.search("CREATE INDEX", sql) and not re.search("CONCURRENTLY", sql),
        "err_msg":
            """A synchronous index creation has been detected. It will block all reads and writes while this is
            occurring. For a small tables (< 100 rows), it should be OK, but a large table it will be very slow
            and can ruin performance. Create the index concurrently for large tables.
            """,
    },
    {
        "code": "DROP_INDEX_SYNC",
        "fn": lambda sql, **kw: re.search("DROP INDEX", sql) and not re.search("CONCURRENTLY", sql),
        "err_msg":
            """A synchronous index deletion has been detected. It will block all reads and writes while this is
            occurring. For a small tables (< 100 rows), it should be OK, but a large table it will be very slow
            and can ruin performance. Create the index concurrently for large tables.
            """,
    },
    {
        "code": "ALTER_COLUMN",
        "fn": lambda sql, **kw: re.search("ALTER TABLE .* MODIFY", sql)
                                or re.search("ALTER TABLE .* ALTER COLUMN .* TYPE", sql),
        "err_msg": (
            "ALTERING columns (Could be backwards incompatible. "
            "Check operation to be sure.)"
        ),
    },
)


def analyse_sql_statements(sql_statements):
    errors = []
    for statement in sql_statements:
        for test in migration_tests:
            if test["fn"](statement, errors=errors):
                logger.debug("Testing {0} -- ERROR".format(statement))
                table_search = re.search("TABLE \"([^\"]*)\"", statement, re.IGNORECASE)
                col_search = re.search("COLUMN \"([^\"]*)\"", statement, re.IGNORECASE)
                err = {
                    "err_msg": test["err_msg"],
                    "code": test["code"],
                    "table": table_search.group(1) if table_search else None,
                    "column": col_search.group(1) if col_search else None,
                }
                errors.append(err)
            else:
                logger.debug("Testing {0} -- PASSED".format(statement))
    return errors

import logging
import re

logger = logging.getLogger(__name__)


migration_tests = (
    {
        "code": "NOT_NULL",
        "fn": lambda sql, **kw: re.search("NOT NULL", sql)
        and not re.search("CREATE TABLE", sql),
        "err_msg": "NOT NULL constraint on columns",
    },
    {
        "code": "DROP_COLUMN",
        "fn": lambda sql, **kw: re.search("DROP COLUMN", sql),
        "err_msg": "DROPPING columns",
    },
    {
        "code": "RENAME_COLUMN",
        "fn": lambda sql, **kw: re.search("ALTER TABLE .* CHANGE", sql)
        or re.search("ALTER TABLE .* RENAME COLUMN", sql),
        "err_msg": "RENAMING columns",
    },
    {
        "code": "RENAME_TABLE",
        "fn": lambda sql, **kw: re.search("RENAME TABLE", sql)
        or re.search("ALTER TABLE .* RENAME TO", sql),
        "err_msg": "RENAMING tables",
    },
    {
        "code": "DROP_TABLE",
        "fn": lambda sql, **kw: re.search("DROP TABLE", sql),
        "err_msg": "DROPPING tables",
    },
    {
        "code": "CREATE_INDEX_SYNC",
        "fn": lambda sql, **kw: re.search("CREATE INDEX", sql) and not re.search("CONCURRENTLY", sql),
        "err_msg": "CREATING INDEX SYNC",
    },
    {
        "code": "DROP_INDEX_SYNC",
        "fn": lambda sql, **kw: re.search("DROP INDEX", sql) and not re.search("CONCURRENTLY", sql),
        "err_msg": "DROP INDEX SYNC",
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
                table_search = re.search("TABLE `([^`]*)`", statement, re.IGNORECASE)
                col_search = re.search("COLUMN `([^`]*)`", statement, re.IGNORECASE)
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


import os
import sys
from sqlalchemy.dialects.mysql import BIT, INTEGER,TINYINT

def parse_module_name_from_filepath(filepath):
    """
    Adds module file path to python path and returns the proper name that eztest should import.
    Most of this was taken from flask github source code
    :type filepath: str
    """
    path = os.path.realpath(filepath)
    if os.path.splitext(path)[1] == '.py':
        path = os.path.splitext(path)[0]

    if os.path.basename(path) == '__init__':
        path = os.path.dirname(path)

    module_name = []

    # move up until outside package structure (no __init__.py)
    while True:
        path, name = os.path.split(path)
        module_name.append(name)

        if not os.path.exists(os.path.join(path, '__init__.py')):
            break

    if sys.path[0] != path:
        sys.path.insert(0, path)
    return '.'.join(module_name[::-1])


def convert_sql_table_to_sqlite_table(table):
    for column in table.columns:
        column.nullable = True
        column.unique = False
        if type(column.type) in [BIT,TINYINT]:
            column.type = INTEGER()
        if getattr(column.type, 'collation', None) is not None:
            column.type = type(column.type)(length=column.type.length)
    table.indexes = set()
    table.constraints = set()

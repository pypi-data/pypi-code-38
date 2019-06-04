from typing import List, Union

from sqlalchemy import text

from peek_plugin_base.storage.AlembicEnvBase import isMssqlDialect, isPostGreSQLDialect


def _createMssqlSqlText(values: List[Union[int, str]]) -> str:
    if not values:
        name = "peekCsvVarcharToTable"  # Either will do

    elif isinstance(values[0], str):
        name = "peekCsvVarcharToTable"

    elif isinstance(values[0], int):
        name = "peekCsvIntToTable"
        values = [str(v) for v in values]

    else:
        raise NotImplementedError("The value supplies isn't a str or int, %s", values[0])

    return text("SELECT * FROM [dbo].[%s]('%s')" % (name, ','.join(values)))


def makeOrmValuesSubqueryCondition(ormSession, column, values: List[Union[int, str]]):
    """ Make Orm Values Subquery

    :param ormSession: The orm session instance
    :param column: The column from the Declarative table, eg TableItem.colName
    :param values: A list of string or int values
    """
    if isPostGreSQLDialect(ormSession.bind):
        return column.in_(values)

    if not isMssqlDialect(ormSession.bind):
        raise NotImplementedError()

    sql = _createMssqlSqlText(values)

    sub_qry = ormSession.query(column)  # Any column, it just assigns a name
    sub_qry = sub_qry.from_statement(sql)

    return column.in_(sub_qry)


def makeCoreValuesSubqueryCondition(engine, column, values: List[Union[int, str]]):
    """ Make Core Values Subquery

    :param engine: The database engine, used to determine the dialect
    :param column: The column, eg TableItem.__table__.c.colName
    :param values: A list of string or int values
    """

    if isPostGreSQLDialect(engine):
        return column.in_(values)

    if not isMssqlDialect(engine):
        raise NotImplementedError()

    sql = _createMssqlSqlText(values)

    return column.in_(sql)


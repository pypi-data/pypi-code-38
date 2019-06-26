from psycopg2 import sql

from . import TowelAttributeError


class SQL:
    CREATE_TABLE = "create table {} "
    SELECT_ALL = "select {}.* from {}"
    LIMIT = sql.SQL("limit %s")
    GET_BY_PK = "select * from {} where id = %s"
    UPDATE = "update {} set "
    REMOVE = "delete from {} "
    REMOVE_BY_ID = REMOVE + " where id = %s"

    OPERATORS = ("<", ">", "<=", ">=", "=", "<>")

    @classmethod
    def INSERT(cls, columns):
        statement = ("insert into {} " + "(" + ", ".join(
            column.column_name for column in columns if column.column_name != "id") + ") values")
        return statement

    @classmethod
    def create_table(cls, model):
        data = [item.sql for item in model.columns() if item.column_name != "id"]
        if not getattr(model, "id"):
            raise TowelAttributeError("ID column was not set")
        data.insert(0, "id SERIAL PRIMARY KEY")
        columns = ', '.join(data)
        return sql.SQL(cls.CREATE_TABLE + "(" + columns + ")").format(sql.Identifier(model.tablename()))

    @classmethod
    def save_model(cls, model):
        values = [item.value for item in model.columns() if item.column_name != "id"]
        placeholders = ', '.join("%s" for _ in range(len(values)))
        return sql.SQL(cls.INSERT(model.columns()) + "(" + placeholders + ") returning id").format(
            sql.Identifier(model.tablename())), values

    @classmethod
    def update(cls, model, **kwargs):
        columns = ', '.join([item + "=%s" for item in kwargs if item != "id"])
        values = list(kwargs.values())
        return sql.SQL(cls.UPDATE + columns).format(
            sql.Identifier(model.tablename())), values

    @classmethod
    def remove(cls, model):
        return sql.SQL(cls.REMOVE).format(sql.Identifier(model.tablename()))

    @classmethod
    def remove_by_id(cls, model):
        return sql.SQL(cls.REMOVE_BY_ID).format(sql.Identifier(model.tablename())), (model.id.value,)

    @classmethod
    def get(cls, model):
        return sql.SQL(cls.GET_BY_PK).format(sql.Identifier(model.tablename()))

    @classmethod
    def select_all(cls, model):
        return sql.SQL(cls.SELECT_ALL).format(sql.Identifier(model.tablename()), sql.Identifier(model.tablename()))

    @classmethod
    def filter(cls, model, column, operator):
        return sql.SQL(" {}.{} " + operator + " %s").format(sql.Identifier(model.tablename()), sql.Identifier(column))

    @classmethod
    def construct_join_clause(cls, join_table, tablename, column_name):
        return sql.SQL(" {}.{} = {}.{} ").format(
            *[sql.Identifier(x) for x in (join_table, "id", tablename, column_name)])

import psycopg2
from psycopg2 import sql
import psycopg2.extras
import psycopg2.errors

from . import TowelOperationalError, TowelAttributeError, SQL, TowelValueError

ident = sql.Identifier


class ObjectManager:
    where_clause = None
    where_values = []
    join_table = None
    if_join = False
    join_clause = None

    def __init__(self, model):
        self.model = model
        self.connection = model.db.connection
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

    def create_table(self):
        self.cursor.execute(SQL.create_table(self.model))
        self.connection.commit()

    def save(self):
        if not self.table_exists:
            self.create_table()
        self._raise_if_not_inst()
        if self.model.id and self.model.id.value:
            if self.get(self.model.id.value):
                raise TowelOperationalError("Can't save model with duplicate id")

        statement, values = SQL.save_model(self.model)
        try:
            self.cursor.execute(statement, values)
        except psycopg2.errors.ForeignKeyViolation as e:
            raise TowelAttributeError(str(e))

        self.model.id.value = self.cursor.fetchone().id

    def update(self, **kwargs):
        if self.if_join:
            raise TowelOperationalError("Towel currently doesn't support updating with join clause")

        self._raise_if_table_doesnt_exist()
        columns = tuple(col.column_name for col in self.model.columns())
        if not all(column in columns for column in kwargs):
            raise TowelAttributeError(f"Not all columns provided are defined in model {self.model.__class__.__name__}")
        if "id" in kwargs:
            raise TowelAttributeError("Can't update 'id' column")

        def update_if_instance():
            for key, value in kwargs.items():
                try:
                    setattr(getattr(self.model, key), "value", value)
                except TowelValueError as e:
                    raise e

            try:
                self.cursor.execute(*SQL.update(self.model, **kwargs))
            except psycopg2.Error as e:
                raise TowelOperationalError(f"{str(e)} was raised during update")

        def update_if_class():
            try:
                self.model(**kwargs)
            except TowelValueError as e:
                raise e

            statement, values = self._concatenate_where_clause(*SQL.update(self.model, **kwargs))

            try:
                self.cursor.execute(statement, values)
            except psycopg2.Error as e:
                raise TowelOperationalError(f"{str(e)} was raised during update")

        if not isinstance(self.model, type):
            update_if_instance()
        else:
            update_if_class()

    def remove(self):
        self._raise_if_table_doesnt_exist()

        if not isinstance(self.model, type):
            try:
                self.cursor.execute(*SQL.remove_by_id(self.model))
            except psycopg2.Error as e:
                raise TowelOperationalError(f"{str(e)} was raised during remove")
        else:
            values = []
            statement, values = self._concatenate_where_clause(SQL.remove(self.model), values,
                                                               for_join_remove=self.if_join)

            self.cursor.execute(statement, values)

    def get_all(self, limit=None):
        self._raise_if_table_doesnt_exist()
        if limit is not None and (not isinstance(limit, int) or limit < 0):
            raise TowelAttributeError("Limit cannot be negative or non-int")

        statement = SQL.select_all(self.model)

        values = []
        statement, values = self._concatenate_where_clause(statement, values, limit)

        self.cursor.execute(statement, values)
        return self.cursor.fetchall()

    def get(self, pk):
        self._raise_if_table_doesnt_exist()
        self.cursor.execute(SQL.get(self.model), (pk,))
        result = self.cursor.fetchone()
        if not result:
            return None
        return self.model.from_namedtuple(result)

    def filter(self, column, operator, value):
        if operator not in SQL.OPERATORS:
            raise TowelAttributeError(f"{operator} is illegal SQL operator ({' '.join(SQL.OPERATORS)})")

        if "__" not in column:
            self._simple_filter(column, operator, value)
        else:
            self._join_filter(column, operator, value)

        return self

    @property
    def table_empty(self):
        self.cursor.execute(sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(self.model.tablename())))
        return bool(self.cursor.fetchone()[0])

    @property
    def table_exists(self):
        self.cursor.execute(sql.SQL("SELECT to_regclass('public.{}');").format(sql.Identifier(self.model.tablename())))
        return self.cursor.fetchone()[0] == self.model.tablename()

    def _join_filter(self, column, operator, value):
        try:
            self.foreign_column, join_column = column.split("__")
        except ValueError:
            raise TowelValueError(f"{column} is not valid column name for filtering")

        # get instance of join model
        model_foreign_column = getattr(self.model, self.foreign_column)
        foreign_inst = model_foreign_column.foreign_entity
        self.join_table = foreign_inst.tablename()

        if not self.join_clause:
            self.join_clause = sql.SQL(" inner join {} on ").format(ident(self.join_table)) + SQL.construct_join_clause(
                self.join_table,
                self.model.tablename(),
                model_foreign_column.column_name)

        self.where_values.append(value)
        statement = SQL.filter(foreign_inst, join_column, operator)

        self._append_where_value(statement)
        self.if_join = True

    def _simple_filter(self, column, operator, value):
        if not any(column == item.column_name for item in self.model.columns()):
            raise TowelAttributeError(f"{column} is not defined in model {self.model.__name__}")

        self.where_values.append(value)

        statement = SQL.filter(self.model, column, operator)

        self._append_where_value(statement)

    def _append_where_value(self, statement):
        if self.where_clause:
            self.where_clause += sql.SQL("and") + statement
        else:
            self.where_clause = statement

    def _reset_where_attrs(self):
        self.where_clause = None
        self.where_values.clear()
        self.join_table = None
        self.if_join = False
        self.join_clause = None
        self.foreign_column = None

    def _raise_if_not_inst(self):
        if isinstance(self.model, type):
            raise TowelValueError("Method can be applied only to model instance")

    def _raise_if_table_doesnt_exist(self):
        if not self.table_exists:
            raise TowelOperationalError("Table doesn't exist")

    def _concatenate_where_clause(self, statement, values, limit=None, for_join_remove=False):
        if self.where_clause:
            if for_join_remove:
                self.join_clause = sql.SQL(" using {} ").format(sql.Identifier(self.join_table))
                self.where_clause += sql.SQL(" and ") + SQL.construct_join_clause(self.join_table,
                                                                                  self.model.tablename(),
                                                                                  self.foreign_column)
            if self.if_join:
                statement += self.join_clause
            statement += sql.SQL(" where ") + self.where_clause
            values.extend(self.where_values)
        elif limit:
            statement += SQL.LIMIT
            values.append(limit)

        self._reset_where_attrs()
        return statement, values

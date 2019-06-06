import sqlite3

from .validations import type_pos_int, type_non_neg_int, expect_in, expect_type, expect_len_range, cast_expect_type
from .shared_exceptions import StatusMessageException


def _process_values(values, processors, column_list, context):
    if not values or not processors:
        return values

    if isinstance(values, (list, tuple)):
        if isinstance(values[0], (list, tuple, dict)):
            return [_process_values(v, processors, column_list, context) for v in values]

        processors = {i: processors[c] for i, c in enumerate(column_list) if c in processors}
        iterator = range(len(values))
        values = list(values)
    else:
        iterator = values.keys()

    for key in iterator:
        if key in processors:
            p_list = processors[key]
            if not isinstance(p_list, (list, tuple)):
                p_list = [p_list]
            for p in p_list:
                values[key] = p(values[key], **context)

    return values


class SQLResult():
    """Result object from SQLite queries"""

    def __init__(self, result_cursor, postprocessors=None, column_list=None):
        self.result_cursor = result_cursor
        self.postprocessors = postprocessors
        self.column_list = column_list

    def _postprocess_values(self, values):
        return _process_values(values, self.postprocessors, self.column_list, context={})

    # This can be used as a iterator, WILL run the postprocessors
    def __iter__(self):
        return self

    def __next__(self):
        return self._postprocess_values(next(self.result_cursor))

    # Convenience functions for getting certain numbers of results, WILL run the postprocessors
    def one_or_none(self):
        return self.one(True)

    def one(self, none_ok=False):
        first_row = self.result_cursor.fetchone()

        if not first_row:
            if not none_ok:
                raise SQLCompositorBadResult('Did not find any results for query, where exactly one was expected')
            return None

        if self.result_cursor.fetchone():
            raise SQLCompositorBadResult('Found too many results for query, where at most one was expected')

        return self._postprocess_values(first_row)

    def all(self):
        return self._postprocess_values(self.result_cursor.fetchall())

    # Built-in functions in sqlite3, note that these DO NOT run the postprocessors, for raw data access
    def lastrowid(self):
        return self.result_cursor.lastrowid

    def fetchone(self):
        return self.result_cursor.fetchone()

    def fetchmany(self, size=None):
        if not size:
            return self.result_cursor.fetchmany()

        return self.result_cursor.fetchmany(size)

    def fetchall(self):
        return self.result_cursor.fetchall()


class SQLiteDB():
    """SQLite Database interface to auto-generate queries and results"""

    def __init__(self, db_path, table_mappers, preprocessors=None, postprocessors=None,
                 enable_foreign_key_constraints=False):
        self.db_path = db_path
        if not table_mappers:
            raise SQLCompositorBadInput('Must define table_mappers to use this interface')
        self.table_mappers = table_mappers
        self.current_connection = None
        self.current_cursor = None
        self.enable_foreign_key_constraints = enable_foreign_key_constraints
        self.preprocessors = preprocessors
        self.postprocessors = postprocessors

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def is_valid_table(self, table_name):
        return table_name in self.table_mappers

    def get_preprocessors(self, table_name):
        if not self.preprocessors:
            return None
        return self.preprocessors.get(table_name)

    def get_postprocessors(self, table_name):
        if not self.postprocessors:
            return None
        return self.postprocessors.get(table_name)

    def select_all(self, table_name):
        return SQLQuery('SELECT', table_name, self).column_list(self.table_mappers[table_name])

    def select(self, table_name, columns):
        return SQLQuery('SELECT', table_name, self).column_list(columns)

    def update(self, table_name):
        return SQLQuery('UPDATE', table_name, self)

    def update_mapped(self, table_name, set_values):
        return self.update(table_name).set_values(set_values)

    def insert(self, table_name, columns):
        return self.insert_into(table_name, columns)

    def insert_mapped(self, table_name, data, autorun=True):
        return self.insert_into_mapped(table_name, data, autorun=autorun)

    def insert_into(self, table_name, columns):
        return SQLQuery('INSERT INTO', table_name, self).column_list(columns)

    def insert_into_mapped(self, table_name, data, autorun=True):
        if isinstance(data, (list, tuple)):
            # Auto-detect column list
            columns = set()
            for row in data:
                columns.update(list(row.keys()))

            return SQLQuery('INSERT INTO', table_name, self).column_list(list(columns)).values_mapped(data, autorun=autorun)
        else:
            return SQLQuery('INSERT INTO', table_name, self).column_list(list(data.keys())).values_mapped(data, autorun=autorun)

    def delete(self, table_name):
        # TODO: Delete-all protection?
        return SQLQuery('DELETE', table_name, self)

    def connection(self):
        if not self.current_connection:
            self.current_connection = sqlite3.connect(self.db_path)

        return self.current_connection

    def cursor(self):
        if not self.current_cursor:
            self.current_cursor = self.connection().cursor()

            if self.enable_foreign_key_constraints:
                self.current_cursor.execute('PRAGMA foreign_keys = ON')

        return self.current_cursor

    def execute(self, query_str, fill_values=None, postprocessors=None, column_list=None):
        cur = self.cursor()
        if not fill_values:
            cur.execute(query_str)
        else:
            cur.execute(query_str, fill_values)
        return SQLResult(cur, postprocessors, column_list)

    def executemany(self, query_str, fill_values, postprocessors=None, column_list=None):
        cur = self.cursor()
        cur.executemany(query_str, fill_values)
        return SQLResult(cur, postprocessors, column_list)

    def rollback(self):
        if not self.current_connection:
            return

        self.current_connection.rollback()

    def in_transaction(self):
        if not self.current_connection:
            return False

        return self.current_connection.in_transaction

    def commit(self, no_changes_ok=False):
        if not self.in_transaction():
            if no_changes_ok:
                return
            raise RuntimeError('No changes in a transaction open for SQLiteDB instance, cannot commit nothing')

        self.current_connection.commit()

    def close(self):
        if not self.current_connection:
            return

        # Default is to NOT commit any changes, be sure to call commit first!
        self.current_connection.close()

        self.current_cursor = None
        self.current_connection = None


class SQLCompositorBadInput(StatusMessageException):
    def __init__(self, message, status_code=None, additional_information=None):
        StatusMessageException.__init__(self, message, status_code, additional_information)


class SQLCompositorBadResult(StatusMessageException):
    def __init__(self, message, status_code=None, additional_information=None):
        StatusMessageException.__init__(self, message, status_code, additional_information)


def _process_single_column_values(values, column, processors, context):
    if not values or not processors:
        return values

    if column in processors:
        p_list = processors[column]
        if not isinstance(p_list, (list, tuple)):
            p_list = [p_list]

        for p in p_list:
            if isinstance(values, (list, tuple)):
                values = [p(v, **context) for v in values]
            else:
                values = p(values, **context)

    return values


def generate_selector(selector, fill_values, valid_columns, processors, context):
    """Generates a selector from the given JSON-style selector"""

    if isinstance(selector, dict):
        if len(selector) != 1:
            raise SQLCompositorBadInput('Each nested selector must have only one logical operator: AND or OR')
        for kind, s_list in selector.items():
            kind = kind.upper()
            expect_type(s_list, (list, tuple), 'selector')
            expect_in(kind, ('AND', 'OR'), 'logical operator')
            return f' {kind} '.join([f'({generate_selector(s, fill_values, valid_columns, processors, context)})' for s in s_list])

    expect_type(selector, (list, tuple), 'selector')
    expect_len_range(selector, 2, 3, 'selector')
    column = selector[0]
    expect_in(column, valid_columns, 'column name')
    operator = selector[1].lower()

    value = None
    value_required = True
    value_expected_types = None
    value_list = False

    if operator in ('eq', '=', '=='):
        sql_operator = '='
    elif operator in ('lt', '<'):
        sql_operator = '<'
    elif operator in ('gt', '>'):
        sql_operator = '>'
    elif operator in ('lte', '<='):
        sql_operator = '<='
    elif operator in ('gte', '>='):
        sql_operator = '>='
    elif operator in ('in'):
        sql_operator = 'IN'
        value_expected_types = (list, tuple)
        value_list = True
    elif operator in ('notin', 'not_in'):
        sql_operator = 'NOT IN'
        value_expected_types = (list, tuple)
        value_list = True
    elif operator in ('like'):
        sql_operator = 'LIKE'
        value_expected_types = str
    elif operator in ('isnull', 'is_null'):
        # TODO: 'is', 'null' or 'is', None options?
        sql_operator = 'IS NULL'
        value_required = False
    elif operator in ('isnotnull', 'is_not_null'):
        sql_operator = 'IS NOT NULL'
        value_required = False
    else:
        raise SQLCompositorBadInput('Unsupported Operator')

    if value_required:
        if len(selector) != 3 or selector[2] is None:
            raise SQLCompositorBadInput(f'Must provide a non-null value for comparison for operator {operator}')
        value = _process_single_column_values(selector[2], column, processors, context)

        if value_expected_types:
            expect_type(value, value_expected_types, f'value for {operator} operator')

        if value_list:
            fill_values.extend(value)  # As this can be user-supplied

            return f'"{column}" {sql_operator} (' + ','.join(['?'] * len(value)) + ')'

        fill_values.append(value)  # As this can be user-supplied

        return f'"{column}" {sql_operator} ?'

    return f'"{column}" {sql_operator}'


# Table to dict mapper for results (multiple rows)
def map_index(index_names, values):
    mapped_values = []

    if not values:
        return mapped_values

    for row in values:
        mapped_values.append(map_index_one_row(index_names, row))

    return mapped_values


def map_index_one_row(index_names, row):
    if row is None:
        return None

    mapped_row = {}
    for i, name in enumerate(index_names):
        if len(row) <= i:
            break
        mapped_row[name] = row[i]

    return mapped_row


# Dict to index mapper for input values (one row at a time)
def unmap_index(index_names, mapped_values):
    values = [None] * len(index_names)

    if not mapped_values:
        return values

    for key, value in mapped_values.items():
        expect_in(key, index_names, 'column name')
        values[index_names.index(key)] = value

    return values


class SQLQuery():
    """Base class for handling and compositing SQL queries"""

    def __init__(self, kind, table_name, db):
        self.kind = kind.upper().strip()
        expect_in(self.kind, ('UPDATE', 'SELECT', 'INSERT INTO', 'DELETE'), 'query kind')

        self.table_name = table_name.strip()

        if not db.is_valid_table(self.table_name):
            raise SQLCompositorBadInput(f'Unknown table: {self.table_name}')

        self.valid_columns = db.table_mappers[self.table_name]

        self.data = {
            'column_list': None,
            'where': None,
            'order_by': None,
            'set_values': None,
            'values': None,
            'limit': None,
            'offset': None,
        }
        self.count_mode = False
        self.many_query = False
        self.fill_values = []

        self.db = db

    def _get_table_map(self):
        return self.db.table_mappers[self.table_name]

    # Validations
    def _validate_clause(self, clause, fill_values):
        if clause.count('?') != len(fill_values):
            raise RuntimeError('Internal Error: Expected equal number of ? substitution elements and fill_values')

    def expect_kind(self, kinds, func_name):
        if not isinstance(kinds, (list, tuple)):
            kinds = [kinds]

        if self.kind not in kinds:
            raise SQLCompositorBadInput(f'Expected kind to be in {kinds} for function {func_name}')

    def _set_query_data_only_once(self, key, value):
        if self.data.get(key) is not None:
            raise SQLCompositorBadInput(f'This query has {key} already set!')

        self.data[key] = value

        return self

    # Functions to be called to compose a query
    def column_list(self, column_list):
        self.expect_kind(('SELECT', 'INSERT INTO'), 'column_list')
        if not isinstance(column_list, (list, tuple)):
            if column_list != '*':
                raise SQLCompositorBadInput('Column list must be a list or *')
            return self._set_query_data_only_once('column_list', self.valid_columns)  # Use the original list here to ensure no ordering mismatches

        for c in column_list:
            if c not in self.valid_columns:
                raise SQLCompositorBadInput(f'Unknown column: {c}')

        self._set_query_data_only_once('column_list', column_list)
        return self

    def where(self, selector):
        """
        Selectors are in the format:
        ['col', 'eq', 5] -> col = 5
        {'and': [
            ['col', 'lt', 6],
            ['a', 'like', '%b%']
        ]} -> col < 6 AND a LIKE %b%
        """
        self.expect_kind(('SELECT', 'UPDATE', 'DELETE'), 'where')

        new_fill_values = []
        clause = generate_selector(selector, new_fill_values, self.valid_columns, self.db.get_preprocessors(self.table_name),
                                   {'db': self.db, 'mode': 'WHERE'})
        self._validate_clause(clause, new_fill_values)

        self._set_query_data_only_once('where', clause)

        self.fill_values.extend(new_fill_values)
        return self

    def get_id(self, row_id):
        # Shortcut for getting a particular ID
        return self.where(['id', 'eq', row_id])

    def _preprocess_values(self, values, mode='INSERT INTO'):
        return _process_values(values, self.db.get_preprocessors(self.table_name), self.data['column_list'],
                               {'db': self.db, 'mode': mode})

    def set_values(self, set_values):
        self.expect_kind('UPDATE', 'set_values')
        if not isinstance(set_values, dict):
            raise SQLCompositorBadInput('Must provide a dictionary of column names to values for set_values')

        for c in set_values.keys():
            if c not in self.valid_columns:
                raise SQLCompositorBadInput(f'Unknown column: {c}')

        self._set_query_data_only_once('set_values', self._preprocess_values(set_values, mode='UPDATE'))
        return self

    def values(self, values, autorun=True):
        self.expect_kind('INSERT INTO', 'values')
        if not self.data['column_list']:
            raise SQLCompositorBadInput('Must set column_list first to the list of columns you wish to insert')

        if not isinstance(values, (list, tuple)):
            raise SQLCompositorBadInput('Must provide a list of values for values in insert statments')

        if isinstance(values[0], (list, tuple)):
            for row in values:
                if len(row) != len(self.data['column_list']):
                    raise SQLCompositorBadInput('Must provide a list of lists each with the same length as the columns provided to insert')
            self.many_query = True

        elif len(values) != len(self.data['column_list']):
            raise SQLCompositorBadInput('Must provide a list with the same length as the columns provided to insert')

        self._set_query_data_only_once('values', self._preprocess_values(values))

        if autorun:
            # Since all data is now available
            return self.run()
        else:
            return self

    def values_mapped(self, values, autorun=True):
        self.expect_kind('INSERT INTO', 'values')
        if not self.data['column_list']:
            raise SQLCompositorBadInput('Must set column_list first to the list of columns you wish to insert')

        if isinstance(values, dict):
            # unmap_index performs column name checking
            values = unmap_index(self.data['column_list'], values)
        elif isinstance(values, (list, tuple)):
            for v in values:
                expect_type(v, dict, 'values_mapped input row dictionary')
            # unmap_index performs column name checking
            values = [unmap_index(self.data['column_list'], v) for v in values]
            self.many_query = True
        else:
            raise SQLCompositorBadInput('Must provide a list of value dicts or one value dict for values_mapped in insert statments')

        self._set_query_data_only_once('values', self._preprocess_values(values))

        if autorun:
            # Since all data is now available
            return self.run()
        else:
            return self

    def order_by(self, columns):
        self.expect_kind('SELECT', 'order_by')
        expect_type(columns, (list, tuple, dict, str), 'order by column(s)')

        if not columns:
            raise SQLCompositorBadInput('Must specify one or more columns to order by')

        if isinstance(columns, (dict, str)):
            columns = [columns]

        order_by_tuples = []

        for c_obj in columns:
            if isinstance(c_obj, str):
                c_obj = {'column': c_obj, 'direction': 'ASC'}

            expect_type(c_obj, dict, 'order_by column/direction object')

            if 'column' not in c_obj:
                raise SQLCompositorBadInput('Complex order_by request must contain a column key '
                                            'and an optional direction key in the input dictionary')
            column = c_obj['column']
            direction = c_obj.get('direction', 'ASC').upper()

            if column not in self.valid_columns:
                raise SQLCompositorBadInput(f'Unknown column: {column}')

            order_by_tuples.append((column, direction))

        self._set_query_data_only_once('order_by', order_by_tuples)
        return self

    def limit(self, value):
        self.expect_kind('SELECT', 'limit')
        value = cast_expect_type(value, type_pos_int, 'LIMIT')

        self._set_query_data_only_once('limit', value)
        return self

    def offset(self, value):
        self.expect_kind('SELECT', 'offset')
        value = cast_expect_type(value, type_non_neg_int, 'OFFSET')

        self._set_query_data_only_once('offset', value)
        return self

    def count(self):
        self.expect_kind('SELECT', 'count')
        if self.count_mode:
            raise SQLCompositorBadInput('Count already set on this query')

        self.count_mode = True
        return self

    # Run and return the result of the query
    def result(self):
        column_list = self.data['column_list']
        escaped_column_list = None
        if column_list:
            escaped_column_list = ','.join([f'"{c}"' for c in column_list])
        where = self.data['where']
        order_by = self.data['order_by']
        limit = self.data['limit']
        offset = self.data['offset']
        values = self.data['values']
        postprocessors = None

        if self.kind == 'SELECT':
            query_str = 'SELECT ' + escaped_column_list + ' FROM ' + self.table_name

            postprocessors = self.db.get_postprocessors(self.table_name)

        elif self.kind == 'UPDATE':
            query_str = 'UPDATE ' + self.table_name + ' SET '

            set_phrases = []
            add_fill_values = []
            for column, value in self.data['set_values'].items():
                set_phrases.append(f'"{column}" = ?')
                add_fill_values.append(value)

            query_str += ','.join(set_phrases)
            add_fill_values.extend(self.fill_values)
            self.fill_values = add_fill_values

        elif self.kind == 'INSERT INTO':
            query_str = 'INSERT INTO ' + self.table_name + '(' + escaped_column_list + ')'

        elif self.kind == 'DELETE':
            query_str = 'DELETE FROM ' + self.table_name

        if where:
            query_str += ' WHERE ' + where

        if order_by:
            query_str += ' ORDER BY ' + ','.join([f'"{c}" {d}' for c, d in order_by])

        if limit:
            query_str += f' LIMIT {limit}'
            if offset is not None:
                query_str += f' OFFSET {offset}'

        if values:
            query_str += ' VALUES (' + ','.join(['?'] * len(column_list)) + ')'
            self.fill_values = values

        if self.count_mode:
            query_str = 'SELECT COUNT(*) FROM (' + query_str + ')'

        if ';' in query_str:
            raise SQLCompositorBadInput('Composite statements are not allowed')

        self._validate_clause(query_str, self.fill_values)

        if self.many_query:
            return self.db.executemany(query_str, self.fill_values, postprocessors, column_list)

        return self.db.execute(query_str, self.fill_values, postprocessors, column_list)

    # For executing a query directly (used for update().set_values().where().run() etc.
    # Insert into can autorun, and all, one, one_or_none forms are used for select
    def run(self):
        return self.result()

    # Convenience functions for different kinds and numbers of results
    def all(self):
        return self.result().all()

    def one(self):
        return self.result().one()

    def scalar(self):
        row = self.result().one()
        if len(row) != 1:
            raise SQLCompositorBadResult(f'Expected a scalar output, got {len(row)} results instead')
        return row[0]

    def one_or_none(self):
        return self.result().one_or_none()

    def all_mapped(self):
        return map_index(self._get_table_map(), self.result())

    def one_mapped(self):
        return map_index_one_row(self._get_table_map(), self.result().one())

    def one_or_none_mapped(self):
        return map_index_one_row(self._get_table_map(), self.result().one_or_none())

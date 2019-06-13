#!/usr/bin/env python3

import copy
import sqlalchemy as sa

from sqlalchemy import or_, and_  # , event
# from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     module = dbapi_connection.__class__.__module__
#     if module == 'sqlite3':
#         print('------------------------------------------->>>')
#         cursor = dbapi_connection.cursor()
#         cursor.execute("PRAGMA journal_mode=WAL")
#         cursor.execute("PRAGMA foreign_keys=ON")
#         cursor.close()


class SSQL(object):
    TEMP_PREFIX = 'tmp_'

    class Error(Exception):
        pass

    def __init__(self, config):
        self.meta = sa.MetaData()
        self.engine = None
        self.config = config

    def init_tables(self):
        meta = sa.MetaData(bind=self.engine)
        meta.reflect()
        for idx, dictable in enumerate(self.config.get_value('tables')):
            self._init_table(meta, dictable)

    def _init_table(self, meta, dictable):
        if dictable['name'] not in meta.tables.keys():
            self._create_table(meta, dictable)
            meta.create_all(self.engine)
        else:
            self._init_columns(meta, dictable)
            if 'migrate' in dictable and 'operation' in dictable['migrate']:
                operation = dictable['migrate']['operation']
                if operation == 'drop':
                    self.drop_columns(meta, dictable)
                elif operation == 'rename':
                    self.rename_columns(meta, dictable)

        if 'migrate' in dictable:
            self.config.delete('migrate', dictable)

    def _create_table(self, meta, dictable):
        tablename = dictable['name']
        columns = dictable['columns']
        args = [tablename, meta]
        for colparams in columns:
            args.append(self.build_column(colparams))
        sa.Table(*args)

    def _init_columns(self, meta, dictable):
        tablename = dictable['name']
        columns = dictable['columns']
        for colparam in columns:
            colname = colparam[0]
            if colname in meta.tables[tablename].columns:
                column = meta.tables[tablename].columns[colname]
                coltype = column.type.__class__.__name__
                if not self.is_valid_type(colparam[1], coltype):
                    emsg = 'Column {cn}: Not Matched Type - {a}, {b}'.format(
                        cn=colname, a=colparam[1], b=coltype)
                    raise SSQL.Error(emsg)
                if coltype in ['VARCHAR', 'CHAR']:
                    coltype = column.type
                    # print('@@@', colname, coltype.collation, coltype.length)
                    length = int(colparam[1][len('String'):])
                    if length != coltype.length:
                        emsg = 'Column {cn}: Not Matched String Length::' \
                            'Expected %d, but %d' % (length, coltype.length)
                        raise SSQL.Error(emsg.format(cn=colname))
                if 'PrimaryKey' in colparam and column.primary_key is False:
                    emsg = 'Column {cn}: Not Set Primary Key Property'
                    raise SSQL.Error(emsg.format(cn=colname))
                if 'Unique' in colparam and column.unique is False:
                    emsg = 'Column {cn}: Not Set Unique Property'
                    raise SSQL.Error(emsg.format(cn=colname))
                if 'NotNull' in colparam and column.nullable is True:
                    emsg = 'Column {cn}: Not Null'
                    raise SSQL.Error(emsg.format(cn=colname))
            else:
                colobj = self.build_column(colparam)
                self.add_column(self.engine, tablename, colobj)

    def is_valid_type(cls, config_type, sql_type):
        dbtypes = {
            'INTEGER':  'Integer',
            'FLOAT':    'Float',
            'BOOLEAN':  'Boolean',
            'DATETIME': 'DateTime',
            'DATE':     'Date',
        }
        if sql_type in ['VARCHAR', 'CHAR']:
            return (config_type.find('String') == 0)
        return dbtypes.get(sql_type) == config_type

    def build_column(self, params):
        dbtypes = {
            'Boolean':  sa.Boolean,
            'DateTime': sa.DateTime,
            'Float':    sa.Float,
            'Integer':  sa.Integer,
            'String':   sa.String,
            'Date':     sa.Date,
        }

        def build_type(coltype, params):
            if coltype.find('String') == 0:
                args = []
                kwargs = {}
                if len('String') == len(coltype):
                    raise SSQL.Error('Need Length of String')
                args.append(int(coltype[len('String'):]))
                if 'CollateNocase' in params:
                    kwargs['collation'] = 'NOCASE'
                return sa.String(*args, **kwargs)
            else:
                try:
                    return dbtypes.get(coltype)()
                except Exception:
                    raise SSQL.Error('Unknown Column Type: {}'.format(coltype))

        params = copy.deepcopy(params)
        args = []
        kwargs = {}
        args.append(params.pop(0))
        coltype = params.pop(0)
        args.append(build_type(coltype, params))
        kwargs['nullable'] = False if 'NotNull' in params else True
        kwargs['primary_key'] = True if 'PrimaryKey' in params else False
        kwargs['unique'] = True if 'Unique' in params else False
        # print(str(params), str(args), str(kwargs))
        return sa.Column(*args, **kwargs)

    def get_table(self, tablename):
        return sa.Table(tablename, self.meta, autoload=True,
                        autoload_with=self.engine)

    def add_column(self, engine, tablename, column):
        colname = column.compile(dialect=engine.dialect)
        coltype = column.type.compile(engine.dialect)
        sql = 'ALTER TABLE %s ADD COLUMN %s %s' % (tablename, colname, coltype)
        # print(sql)
        engine.execute(sql)

    def _drop_columns(self, meta, dictable, colnames):
        # BEGIN TRANSACTION;
        # ## XXX: This function worked, but lost each the columns property !!
        # ## CREATE TABLE t1_backup AS SELECT a, b FROM t1;
        # CREATE TABLE t1_backup ( columns with property )
        # INSERT INTO t1_backup SELECT a, b FROM t1;
        # DROP TABLE t1;
        # ALTER TABLE t1_backup RENAME TO t1;
        # COMMIT;
        tablename = dictable['name']
        dictable['name'] = self.TEMP_PREFIX + tablename
        sqls = ['INSERT INTO tmp_{tn} SELECT {cns} FROM {tn}',
                'DROP TABLE {tn}',
                'ALTER TABLE tmp_{tn} RENAME TO {tn}']
        form = {
            'tn':   tablename,
            'ttn':  dictable['name'],
            'cns':  ','.join(colnames)
        }
        # Check to exist tmp_tablename
        try:
            self.get_table(form['ttn'])
            emsg = 'Already Exists Table "{ttn}"'
            raise SSQL.Error(emsg.format(**form))
        except sa.exc.NoSuchTableError:
            self._create_table(meta, dictable)
            meta.create_all(self.engine)

        self.session.begin_nested()
        try:
            for sql in sqls:
                self.session.execute(sql.format(**form))
            self.session.commit()
        except Exception:
            self.session.rollback()
        # Restore the name of table
        dictable['name'] = tablename

    def drop_columns(self, meta, dictable):
        '''It handles columns of a table to the process of dropping and adding,
        concurrently.'''
        remains = []
        for colparam in dictable['columns']:
            remains.append(colparam[0])
        self._drop_columns(meta, dictable, remains)

    def rename_columns(self, meta, dictable):
        '''It handles columns of a table to the process of dropping, renaming,
        and adding, concurrently.'''
        remains = []
        renpool = dictable['migrate']['columns']
        for colparam in dictable['columns']:
            if colparam[0] in renpool:
                remains.append(renpool[colparam[0]])
            else:
                remains.append(colparam[0])
        self._drop_columns(meta, dictable, remains)


class SSimpleDB(SSQL):
    SQL_ECHO = False
    OP_AND = 'and'
    OP_OR = 'or'
    SQL_PAGE = 'page'
    SQL_SIZE = 'size'
    SQL_V_PAGE = 0
    SQL_V_SIZE = 5

    def __init__(self, dbpath, config):
        super(SSimpleDB, self).__init__(config)
        self.engine = sa.create_engine(
            'sqlite:///{db}'.format(db=dbpath), echo=self.SQL_ECHO)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        if self.session.bind.dialect.name == 'sqlite':
            self.session.execute("PRAGMA journal_mode=WAL")
            self.session.execute("PRAGMA foreign_keys=ON")
            self.session.commit()
        self.init_tables()

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
        if self.config and hasattr(self.config, 'store'):
            self.config.store()

    def to_sql(self, o):
        return str(o.compile(compile_kwargs={"literal_binds": True}))

    def _get_columns(self, table, colnames):
        columns = []
        for col in colnames:
            if col in table.c:
                columns.append(table.c[col])
        return columns if columns else table.c

    def get_colnames(self, tablename):
        table = self.get_table(tablename)
        return [x.name for x in table.c]

    def _append_wheres(self, qo, table, **kwargs):
        wheres = kwargs.pop('wheres', {})
        operate = kwargs.pop('operate', self.OP_AND)
        _op = {
            self.OP_AND:    and_,
            self.OP_OR:     or_,
        }
        if wheres:
            filters = []
            for k, v in wheres.items():
                # column = sa.sql.column(k)
                column = table.c[k]
                is_str = column.type.__class__.__name__ in ['VARCHAR', 'CHAR']
                if type(v) is list:
                    _o = None
                    for _v in v:
                        if _o is None:
                            if is_str:
                                _o = or_(column.like('%{}%'.format(_v)))
                            else:
                                _o = or_(column == _v)
                        else:
                            if is_str:
                                _o = or_(column.like('%{}%'.format(_v)), _o)
                            else:
                                _o = or_(column == _v, _o)
                    if _o is not None:
                        filters.append(_o)
                else:
                    if is_str:
                        colike = column.like('%{}%'.format(v))
                        filters.append(_op[operate](colike))
                    else:
                        filters.append(_op[operate](column == v))
            qo = qo.where(_op[operate](*filters))
        return qo

    def _build_query(self, table, *args, **kwargs):
        columns = self._get_columns(table, args)

        qo = sa.sql.select(columns)
        qo = self._append_wheres(qo, table, **kwargs)
        return qo

    def upsert(self, tablename, **kwargs):
        tbl = self.get_table(tablename)
        data = kwargs.get('data')
        only_insert = kwargs.get('only_insert', False)
        rv = False
        pk = next(iter(data))
        # pk_column = sa.sql.column(pk)
        pk_column = tbl.c[pk]

        qc = sa.sql.select([tbl.c[pk]]).where(pk_column == data[pk])
        qi = sa.insert(tbl).values(**data)
        qu = sa.update(tbl).values(**data).where(pk_column == data[pk])
        self.session.begin_nested()
        try:
            item = self.session.query(qc).first()
            if item is None:
                self.session.execute(qi)
                rv = True
            else:
                if only_insert:
                    rv = False
                else:
                    self.session.execute(qu)
                    rv = True
            self.session.commit()
        except Exception:
            self.session.rollback()
        return rv

    def upsert_array(self, tablename, **kwargs):
        '''
        param data - If the content of the array had mixed in the 'only_insert'
                     mode, it updates only non-existent data.
        '''
        tbl = self.get_table(tablename)
        arr_data = kwargs.get('data')
        only_insert = kwargs.get('only_insert', False)

        executed_count = 0
        self.session.begin_nested()
        for data in arr_data:
            pk = next(iter(data))
            pk_column = tbl.c[pk]
            qc = sa.sql.select([tbl.c[pk]]).where(pk_column == data[pk])
            qi = sa.insert(tbl).values(**data)
            qu = sa.update(tbl).values(**data).where(pk_column == data[pk])
            try:
                item = self.session.query(qc).first()
                if item is None:
                    self.session.execute(qi)
                    executed_count += 1
                else:
                    if only_insert:
                        continue
                    else:
                        self.session.execute(qu)
                        executed_count += 1
            except Exception:
                self.session.rollback()
                return False
        self.session.commit()
        return True if executed_count > 0 else False

    def query(self, tablename, *args, **kwargs):
        size = kwargs.pop(self.SQL_SIZE, self.SQL_V_SIZE)
        page = kwargs.pop(self.SQL_PAGE, self.SQL_V_PAGE)

        tbl = self.get_table(tablename)
        qo = self._build_query(tbl, *args, **kwargs)
        qo = qo.limit(size)
        qo = qo.offset(page*size)

        try:
            return self.session.query(qo).all()
        except Exception:
            raise SSimpleDB.Error('Query: {}'.format(self.to_sql(qo)))

    def count(self, tablename, *args, **kwargs):
        tbl = self.get_table(tablename)
        qo = self._build_query(tbl, *args, **kwargs)
        try:
            return self.session.query(qo).count()
        except Exception:
            raise SSimpleDB.Error('Count: {}'.format(self.to_sql(qo)))

    def vacuum(self):
        if self.session.bind.dialect.name == 'sqlite':
            self.session.execute('VACUUM')
            return
        raise SSimpleDB.Error('Not Implemented to VACCUM')

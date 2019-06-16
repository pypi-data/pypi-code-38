from sqlalchemy import MetaData, text, and_
from sqlalchemy.sql.expression import select, delete
from contextlib import contextmanager
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
import datetime


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()

        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                fields[field] = obj.__getattribute__(field)
            return fields

        return json.JSONEncoder.default(self, obj)


def escape(key):
    return "`%s`" % key


def sql_page(sql, page, limit):
    page = int(page)
    limit = int(limit)
    return '%s limit %d offset %d' % (sql, limit, (page-1)*limit)


def sql_count(sql):
    b = sql.lower()
    p1 = 'select '
    p2 = ' from '
    idx1 = b.find(p1)
    idx2 = b.find(p2)
    return sql[0: idx1 + len(p1)] + 'count(0) as total' + sql[idx2:]


class Dict(dict): # dynamic property support, such as d.name
    def __getattr__(self, name):
        if name in self: return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        self.pop(name, None)

    def __getitem__(self, key):
        if key not in self: return None
        return dict.__getitem__(self, key)


class Db:
    def __init__(self, engine, reflect=True):
        self.engine = engine
        self.tables = {}
        self.meta = MetaData()
        if reflect:
            self.reflect()

    def reflect(self):
        self.meta.reflect(bind=self.engine)
        self.tables = self.meta.tables

    @contextmanager
    def session(self):
        """Provide a transactional scope around a series of operations."""

        sa_conn = self.engine.connect()

        tx = sa_conn.begin()
        try:
            connection = Connection(sa_conn, self.tables)
            yield connection
            tx.commit()
        except:
            tx.rollback()
            raise
        finally:
            pass
            sa_conn.close()

    def query(self, sql, converter=None, **kvargs):
        with self.session() as s:
            return s.query(sql, converter, **kvargs)

    def query_page(self, sql, converter=None, **kvargs):
        with self.session() as s:
            return s.query_page(sql, converter, **kvargs)

    def query_one(self, sql, converter=None, **kvargs):
        with self.session() as s:
            return s.query_one(sql, converter, **kvargs)

    def execute(self, sql, **kvargs):
        with self.session() as s:
            return s.execute(sql, **kvargs)

    def add(self, table, json_data):
        with self.session() as s:
            return s.add(table, json_data)

    def add_many(self, table, data):
        with self.session() as s:
            return s.add_many(table, data)

    def merge(self, table, json_data):
        with self.session() as s:
            return s.merge(table, json_data)

    def save(self, table, json_data):
        with self.session() as s:
            return s.save(table, json_data)

    def delete(self, table, key):
        with self.session() as s:
            return s.delete(table, key)

    def one(self, table, key, c=None):
        with self.session() as s:
            return s.one(table, key, c)

    def list(self, table, p=0, n=100, c=None, key=None, key_name=None):
        with self.session() as s:
            return s.list(table, p=p, n=n, c=c, key=key, key_name=key_name)


class Connection:
    def __init__(self, conn, tables):
        self.connection = conn
        self.tables = tables

    def query(self, sql, converter=None, **kvargs):
        return self._query(sql, converter, **kvargs)

    def query_page(self, sql, converter=None, **kvargs):
        page = kvargs.get('page') or 1
        limit = kvargs.get('limit') or 20
        do_count = kvargs.get('do_count') # 0--only data, 1/None--count + data, 2--only count
        if do_count is None:
            do_count = 1

        total, data = None, None
        if do_count >= 1:
            sql_c = sql_count(sql)
            res = self.query_one(sql_c, converter, **kvargs)
            total = res.total
        if do_count <= 1:
            sql_p = sql_page(sql, page, limit)
            sql_p = text(sql_p)
            data = self._query(sql_p, converter, **kvargs)
        return Dict({
            'total': total,
            'page': page,
            'limit': limit,
            'data': data
        })

    def _query(self, s, converter=None, **kvargs):
        if isinstance(s, str):
            s = text(s)

        rs = self.connection.execute(s, **kvargs)

        def c(row):
            if not converter:
                r = Dict(row)
                sub_dict = {}

                for name in r:
                    bb = name.split('.')  # handle . for layer object
                    key = None
                    if len(bb) > 1:
                        obj_name, key = bb
                        obj = sub_dict.get(obj_name)
                        if not obj:
                            sub_dict[obj_name] = obj = {}

                    v = r[name]
                    if isinstance(v, bytes):
                        if len(v) == 1:
                            v = int(v[0])
                    if key:
                        obj[key] = v
                    else:
                        r[name] = v

                r.update(sub_dict)
                return r
            return converter(r)

        return [c(row) for row in rs]

    def query_one(self, sql, converter=None, **kvargs):
        res = self.query(sql, converter, **kvargs)
        if len(res) > 0: return res[0]

    def execute(self, sql, **kvargs):
        if isinstance(sql, str):
            sql = text(sql)
        return self.connection.execute(sql, **kvargs)

    def _check_table(self, table):
        if table not in self.tables:
            raise Exception('Table(%s) Not Found' % table)
        return self.tables[table]

    def _primary_key(self, table):
        t = self._check_table(table)
        if len(t.primary_key) != 1:
            raise Exception('Table(%s) primary key not single' % table)
        for c in t.primary_key:
            return t, c

    def _table_and_column(self, s):
        bb = s.split('.')
        if len(bb) != 2:
            raise Exception('Invalid table and column string: %s' % s)
        t = self._check_table(bb[0])
        if bb[1] not in t.c:
            raise Exception('Column(%s) not in Table(%s)' % (bb[1], bb[0]))
        return t, bb[1]

    def _batch_query(self, t, col_name, value_set):
        value_set = list(value_set)
        if len(value_set) == 1:
            s = select([t]).where(t.c[col_name] == value_set[0])
        else:
            s = select([t]).where(t.c[col_name].in_(value_set))
        data = self._query(s)
        res = {}
        for row in data:
            k = row[col_name]
            if k not in res:
                res[k] = [row]
            else:
                res[k].append(row)
        return res

    def delete(self, table, key):
        t, c_key = self._primary_key(table)
        s = delete(t).where(t.c[c_key.name] == key)
        self.connection.execute(s)

    def one(self, table, key, c=None):
        res = self.list(table, key=[key], c=c)
        if res and len(res) >= 1:
            return res[0]

    def list(self, table, p=0, n=100, c=None, key=None, key_name=None):
        """
        @param table: table mapping name(table raw name by default)
        @param p: page index
        @param n: size of page
        @param c: column list
        @param key: key list or single key
        @param key_name: replace the primary key if set
        """
        t = self._check_table(table)
        c_list = [t]
        if c:
            if not isinstance(c, (list, tuple)):
                c = [c]
            c_list = [t.c[name] for name in c if name in t.c]

        s = select(c_list)
        if key:
            if not key_name:
                _, k = self._primary_key(table)
                key_name = k.name
            if not isinstance(key, (list, tuple)):
                key = [key]

            if len(key) == 1:
                s = s.where(t.c[key_name].op('=')(key[0]))
            else:
                s = s.where(t.c[key_name].in_(key))
        else:
            if n:
                page = int(p)
                page_size = int(n)
                s = s.limit(page_size)
                s = s.offset(page * page_size)

        return self._query(s)

    def add(self, table, json_data):
        self._check_table(table)

        t = self.tables[table]
        sql = t.insert()
        data = Dict({key: json_data[key] for key in json_data if key in t.c})
        res = self.connection.execute(sql, data)
        inserted_keys = res.inserted_primary_key
        i = 0
        for c in t.primary_key:
            if i >= len(inserted_keys):
                break
            data[c.name] = inserted_keys[i]
            i += 1
        return data

    def add_many(self, table, data):
        self._check_table(table)

        if not isinstance(data, (tuple, list)):
            data = [data]
        data_array = []
        for d in data:
            obj = {key: d[key] for key in d if key in table.c}
            data_array.append(obj)

        t = self.tables[table]
        res = self.connection.execute(t.insert(), data_array)
        return res.rowcount

    def merge(self, table, json_data):
        self._check_table(table)

        t = self.tables[table]
        values, where = {}, []
        for key in json_data:
            if key not in t.c:
                continue
            if key in t.primary_key:
                cond = t.c[key] == json_data[key]
                where.append(cond)
            else:
                values[key] = json_data[key]
        if len(where) == 0:
            raise Exception("Missing database primary key in merge action")

        sql = t.update().where(and_(*where)).values(**values)
        return self.connection.execute(sql).rowcount

    def save(self, table, json_data):
        self._check_table(table)

        update = False
        t = self.tables[table]
        for key in json_data:
            if key in t.primary_key:
                update = True
                sql = t.select().where(t.c[key] == json_data[key])
                res = self.query_one(sql)
                if not res:
                    update = False
                break
        if update:
            return self.merge(table, json_data)
        return self.add(table, json_data)

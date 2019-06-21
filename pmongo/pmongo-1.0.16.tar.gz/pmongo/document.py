# -*- coding: UTF-8 -*
'''
Created on 2018-06-15

@author: trb
'''

from pymongo import ASCENDING, DESCENDING
import six


class Manager(object):
    def __init__(self, db=None, model=None):
        self.db = db
        self.model = model

    def find(self, *args, **kwargs):
        query = QuerySet(self)
        if args or kwargs:
            query = query.find(*args, **kwargs)
        return query

    def create(self, **kwargs):
        '''Create and save'''
        obj = self.model(**kwargs)
        obj.save()
        return obj

    @property
    def colname(self):
        '''collection name'''
        return getattr(self.model, '__table__', self.model.__name__).lower()

    def all(self):
        return self.find().all()

    def get(self, *args, **kwargs):
        return self.find().get(*args, **kwargs)

    def save(self, obj, db=None, update_fields=None):
        data = obj.data
        col = (db or self.db)[self.colname]
        if '_id' in data:
            if update_fields != None:
                if update_fields:
                    updata = {k: data[k] for k in update_fields if k in data}
                    col.update({'_id': self._wrap_objid(data['_id'])}, {'$set': updata})
            else:
                col.save(data)
        else:
            docid = col.insert(data)
            data['_id'] = docid

    def unset(self, filter, fields, db=None):
        (db or self.db)[self.colname].update(filter, {'$unset': {k: "" for k in fields}})

    def __repr__(self):
        return '%s@%s#%s' % (self.__class__.__name__, self.db, self.model)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__str__()

    def _wrap_query(self, q):
        return q

    def _wrap_objid(self, v):
        from bson import ObjectId
        if type(v) == dict:
            return {
                nk: self._wrap_objid(nv) for nk, nv in v.items()
            }
        elif type(v) in [list, type, set]:
            return [self._wrap_objid(nv) for nv in v]
        elif not isinstance(v, ObjectId):
            return ObjectId(str(v))
        else:
            return v


class QuerySet(object):
    def __init__(self, manager=None):
        self.manager = manager
        self.chain = []
        self.sort = None
        self._values = None

    def __copy__(self):
        query = type(self)(self.manager)
        query.chain = [r for r in self.chain]
        query.sort = self.sort
        query._values = self._values
        return query

    def _wrap_query(self, q):
        return self.manager._wrap_query(q)

    def find(self, *args, **kwargs):
        query = self.__copy__()
        if args:
            query.chain.append(self._wrap_query(args[0]))
        if kwargs:
            query.chain.append(self._wrap_query(kwargs))
        return query

    def first(self):
        return self.new_obj(data=self.col.find_one(self.query))

    def delete(self):
        return self.col.remove(self.query)['n']

    def exists(self):
        return True if self.count() else False

    def count(self):
        return self.col.find(self.query).count()

    def all(self):
        return list(self)

    def get(self, *args, **kwargs):
        return self.find(_id=(args[0])).first() if args else self.find(**kwargs).first()

    def update(self, *args, **kwargs):
        ope = args[0] if args else ({'$set': kwargs} if kwargs else None)
        if ope:
            return self.col.update_many(self.query, ope).modified_count
        else:
            return 0

    @property
    def col(self):
        return self.manager.db[self.manager.colname]

    @property
    def query(self):
        q = {}
        for c in self.chain:
            q.update(c)
        if q.get('id'):
            q['_id'] = q.pop('id')
        if q.get('_id'):
            q['_id'] = self.manager._wrap_objid(q['_id'])
        return q

    def to_json(self):
        return list(self)

    def new_obj(self, data=None):
        return self.manager.model(data) if data != None else None

    def get_cursor(self):
        if type(self._values) == dict:
            fds = self._values
        elif self._values:
            fds = {k: 1 for k in self._values}
        else:
            fds = None
        cursor = self.col.find(self.query, fds)
        meta = getattr(self.manager.model, 'Meta', None)
        if meta and getattr(meta, 'ordering', None):
            sort = tuple(meta.ordering)
        else:
            sort = None
        if self.sort:
            sort = self.sort
        if sort:
            sorts = [(f[1:], DESCENDING) if f[0] == '-' else (f, ASCENDING) for f in sort]
            if len(sorts):
                cursor = cursor.sort(sorts)
            else:
                cursor = cursor.sort(*sorts[0])
        return cursor

    def __iter__(self):
        for data in self.get_cursor():
            yield self.new_obj(data=data)

    def __getitem__(self, item):
        if type(item) == slice:
            return map(self.new_obj, self.get_cursor()[item])
        else:
            return self.new_obj(self.get_cursor()[item])

    def order_by(self, *args):
        query = self.__copy__()
        query.sort = args
        return query

    def values(self, *args, **kwargs):
        query = self.__copy__()
        query._values = args or kwargs
        return query


class BaseDocument(type):
    def __new__(cls, name, parents, attrs):
        ntype = type.__new__(cls, name, parents, attrs)
        ntype.objects = type(ntype.objects)(getattr(ntype, 'db', None), ntype)
        return ntype

    objects = Manager(None, None)


class Document(six.with_metaclass(BaseDocument)):
    def __init__(self, *args, **kwargs):
        if args:
            self.data = args[0]
        else:
            self.data = kwargs

    def __getitem__(self, key):
        # return self.data.get(key)
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return self.data.__contains__(item)

    def get(self, key, d=None):
        return self.data.get(key, d)

    def __repr__(self):
        return '%s[%s]' % (self.__class__.__name__, self.data)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__str__()

    def __delitem__(self, key):
        return self.data.__delitem__(key)

    def to_json(self):
        return self.data

    def save(self, db=None, update_fields=None):
        self.objects.save(self, db=db, update_fields=update_fields)

    def update(self, d):
        self.data.update(d)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    @property
    def id(self):
        return self.data['_id'] if self.data and '_id' in self.data else None

    @id.setter
    def id(self, val):
        if self.data and '_id' in self.data:
            del self.data['_id']

    def unset(self, keys, db=None):
        for k in keys:
            if k not in self.data:
                continue
            del self.data[k]
        if keys and self.id:
            from bson import ObjectId
            return self.objects.unset({'_id': ObjectId(self.id) if isinstance(self.id, six.string_types) else self.id}, keys, db=db)

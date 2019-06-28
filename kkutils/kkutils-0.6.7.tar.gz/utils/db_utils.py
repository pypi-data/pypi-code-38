#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 11:24:17
'''
import asyncio
import os
from urllib.parse import quote_plus

import aioredis
import pymongo
import redis
from motor import core
from motor.docstrings import get_database_doc
from motor.frameworks import asyncio as asyncio_framework
from motor.metaprogramming import AsyncCommand
from motor.metaprogramming import create_class_with_framework
from motor.metaprogramming import DelegateMethod

from .utils import Dict

__all__ = ['Mongo', 'MongoClient', 'Redis', 'AioRedis', 'Motor', 'MotorClient']


class Collection(pymongo.collection.Collection):

    def find(self, *args, **kwargs):
        kwargs.update({'no_cursor_timeout': True})
        return pymongo.cursor.Cursor(self, *args, **kwargs)

    @property
    def seq_id(self):
        ret = self.database.ids.find_one_and_update({'_id': self.name},
                                                    {'$inc': {'seq': 1}},
                                                    upsert=True,
                                                    projection={'seq': True, '_id': False},
                                                    return_document=True)
        return ret['seq']


class Database(pymongo.database.Database):

    def __getitem__(self, name):
        return Collection(self, name)

    # def _fix_outgoing(self, son, collection):
    #     return DictWrapper(super(Database, self)._fix_outgoing(son, collection))


class MongoClient(pymongo.MongoClient):

    def __init__(self, **kwargs):
        env = 'MONGO_LOC' if kwargs.pop('loc', False) and os.environ.get('MONGO_LOC') else 'MONGO_URI'
        if any([key in kwargs for key in ['host', 'port', 'user', 'pwd']]):
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 27017)
            user = kwargs.pop('user', None)
            pwd = kwargs.pop('pwd', None)
            uri = f"mongodb://{quote_plus(user)}:{quote_plus(pwd)}@{host}:{port}" if user and pwd else f"mongodb://{host}:{port}"
        elif 'uri' in kwargs:
            uri = kwargs.pop('uri')
        elif env in os.environ:
            uri = os.environ.get(env, 'mongodb://localhost:27017')
        else:
            host = os.environ.get('MONGO_HOST', 'localhost')
            port = os.environ.get('MONGO_PORT', 27017)
            user = os.environ.get('MONGO_USER', None)
            pwd = os.environ.get('MONGO_PWD', None)
            uri = f"mongodb://{quote_plus(user)}:{quote_plus(pwd)}@{host}:{port}" if user and pwd else f"mongodb://{host}:{port}"

        kwargs.setdefault('document_class', Dict)
        super(MongoClient, self).__init__(uri, **kwargs)

    def __getitem__(self, name):
        return Database(self, name)

    def __getattr__(self, name):
        return Database(self, name)


class Mongo(Database):

    def __init__(self, db='test', **kwargs):
        client = MongoClient(**kwargs)
        super(Mongo, self).__init__(client, db)


class AgnosticCollection(core.AgnosticCollection):
    __delegate_class__ = Collection

    def __init__(self, database, name, codec_options=None,
                 read_preference=None, write_concern=None, read_concern=None,
                 _delegate=None):
        db_class = create_class_with_framework(
            AgnosticDatabase, self._framework, self.__module__)

        if not isinstance(database, db_class):
            raise TypeError("First argument to MotorCollection must be "
                            "MotorDatabase, not %r" % database)

        delegate = _delegate or Collection(
            database.delegate, name, codec_options=codec_options,
            read_preference=read_preference, write_concern=write_concern,
            read_concern=read_concern)

        super(core.AgnosticBaseProperties, self).__init__(delegate)
        self.database = database


class AgnosticDatabase(core.AgnosticDatabase):
    __delegate_class__ = Database

    create_collection = AsyncCommand().wrap(Collection)
    get_collection = DelegateMethod().wrap(Collection)

    def __init__(self, client, name, **kwargs):
        self._client = client
        delegate = kwargs.get('_delegate') or Database(
            client.delegate, name, **kwargs)

        super(core.AgnosticBaseProperties, self).__init__(delegate)

    def __getitem__(self, name):
        collection_class = create_class_with_framework(
            AgnosticCollection, self._framework, self.__module__)

        return collection_class(self, name)


class AgnosticClient(core.AgnosticClient):
    __delegate_class__ = MongoClient
    get_database = DelegateMethod(doc=get_database_doc).wrap(Database)

    def __getitem__(self, name):
        db_class = create_class_with_framework(
            AgnosticDatabase, self._framework, self.__module__)

        return db_class(self, name)


def create_asyncio_class(cls):
    asyncio_framework.CLASS_PREFIX = ''
    return create_class_with_framework(cls, asyncio_framework, 'db_utils')


MotorClient = create_asyncio_class(AgnosticClient)
MotorDatabase = create_asyncio_class(AgnosticDatabase)
MotorCollection = create_asyncio_class(AgnosticCollection)


class Motor(MotorDatabase):

    def __init__(self, db='test', **kwargs):
        client = MotorClient(**kwargs)
        super(Motor, self).__init__(client, db)


class Redis(redis.StrictRedis):

    def __init__(self, **kwargs):
        if any([key in kwargs for key in ['host', 'port', 'password', 'db']]):
            kwargs.setdefault('host', 'localhost')
            kwargs.setdefault('port', 6379)
            kwargs.setdefault('password', None)
            kwargs.setdefault('db', 0)
        elif 'REDIS_URI' in os.environ:
            uri = os.environ['REDIS_URI']
            assert uri.startswith('redis://')
            arr = uri[8:].split('@', 2)
            kwargs['password'] = arr[0][1:] if len(arr) == 2 else None
            arr = arr[-1].split(':', 2)
            kwargs['host'] = arr[0]
            arr = arr[-1].split('/', 2)
            kwargs['db'] = int(arr[1]) if len(arr) == 2 else 0
            kwargs['port'] = int(arr[0])
        else:
            kwargs['host'] = os.environ.get("REDIS_HOST", 'localhost')
            kwargs['port'] = int(os.environ.get("REDIS_PORT", 6379))
            kwargs['password'] = os.environ.get("REDIS_PWD", None)
            kwargs['db'] = int(os.environ.get("REDIS_DB", 0))

        kwargs.setdefault('decode_responses', True)
        pool = redis.ConnectionPool(**kwargs)
        super().__init__(connection_pool=pool)

    def clear(self, pattern='*'):
        if pattern == '*':
            self.flushdb()
        else:
            keys = [x for x in self.scan_iter(pattern)]
            if keys:
                self.delete(*keys)


class AioRedis(aioredis.Redis):

    def __init__(self, **kwargs):
        if any([key in kwargs for key in ['host', 'port', 'password', 'db']]):
            kwargs.setdefault('host', 'localhost')
            kwargs.setdefault('port', 6379)
            kwargs.setdefault('password', None)
            kwargs.setdefault('db', 0)
        elif 'REDIS_URI' in os.environ:
            uri = os.environ['REDIS_URI']
            assert uri.startswith('redis://')
            arr = uri[8:].split('@', 2)
            kwargs['password'] = arr[0][1:] if len(arr) == 2 else None
            arr = arr[-1].split(':', 2)
            kwargs['host'] = arr[0]
            arr = arr[-1].split('/', 2)
            kwargs['db'] = int(arr[1]) if len(arr) == 2 else 0
            kwargs['port'] = int(arr[0])
        else:
            kwargs['host'] = os.environ.get("REDIS_HOST", 'localhost')
            kwargs['port'] = int(os.environ.get("REDIS_PORT", 6379))
            kwargs['password'] = os.environ.get("REDIS_PWD", None)
            kwargs['db'] = int(os.environ.get("REDIS_DB", 0))

        kwargs.setdefault('encoding', 'utf8')
        loop = kwargs.get('loop', asyncio.get_event_loop())
        if not loop.is_running():
            host, port = kwargs.pop('host'), kwargs.pop('port')
            self._pool = loop.run_until_complete(aioredis.create_pool((host, port), **kwargs))
            super().__init__(self._pool)
        else:
            self._kwargs = kwargs

    async def init(self):
        host, port = self._kwargs.pop('host'), self._kwargs.pop('port')
        self._pool = await aioredis.create_pool((host, port), **self._kwargs)
        super().__init__(self._pool)

    async def finish(self):
        super().close()
        await self.wait_closed()

    async def set(self, name, value, ex=None, px=None, nx=False):
        if ex is not None:
            await super().setex(name, ex, value)
        elif px is not None:
            await super().psetex(name, px, value)
        elif nx:
            await super().setnx(name, value)
        else:
            await super().set(name, value)

    async def clear(self, pattern='*'):
        if pattern == '*':
            await self.flushdb()
        else:
            keys = []
            async for key in self.iscan(match=pattern):
                keys.append(key)
            if keys:
                await self.delete(*keys)


# import torndb
# class Mysql(torndb.Connection):
#
#     def __init__(self, db='pua', **kwargs):
#         kwargs.setdefault('time_zone', '+08:00')
#         kwargs['database'] = db
#         super(Mysql, self).__init__(**kwargs)

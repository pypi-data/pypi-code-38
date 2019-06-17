#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import copy

import pytz
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
from flask import current_app, request
from pymongo import (
    IndexModel,
    ASCENDING,
    DESCENDING,
    GEO2D,
    GEOHAYSTACK,
    GEOSPHERE,
    HASHED,
    TEXT,
)

__version__ = "0.3.0"

INDEX_NAMES = dict(
    asc=ASCENDING,
    ascending=ASCENDING,
    desc=DESCENDING,
    descending=DESCENDING,
    geo2d=GEO2D,
    geohaystack=GEOHAYSTACK,
    geosphere=GEOSPHERE,
    hashed=HASHED,
    text=TEXT,
)
SORT_NAMES = dict(
    asc=ASCENDING, ascending=ASCENDING, desc=DESCENDING, descending=DESCENDING
)


def get_sort(sort, for_index=False):
    if sort is None or isinstance(sort, list) and not for_index:
        return sort

    names = INDEX_NAMES if for_index else SORT_NAMES
    sorts = []
    for items in sort.strip().split(";"):  # ; for many indexes
        items = items.strip()
        if items:
            lst = []
            for item in items.split(","):
                item = item.strip()
                if item:
                    if " " in item:
                        field, _sort = item.replace("  ", " ").split(" ")[:2]
                        lst.append((field, names[_sort.lower()]))
                    else:
                        lst.append((item, names["asc"]))

            if lst:
                sorts.append(lst)

    return sorts[0] if len(sorts) == 1 else sorts


def get_uniq_spec(fields=[], doc={}):
    specs = []
    for field in fields:
        spec = {}
        for k in [f.strip() for f in field.split(",") if f.strip()]:
            if k in doc:
                spec[k] = doc[k]

        if spec:
            specs.append(spec)

    return {"$or": specs} if specs else None


class BaseMixin:
    @property
    def id(self):
        return self["_id"]

    @classmethod
    def is_valid_oid(cls, oid):
        return ObjectId.is_valid(oid)

    @classmethod
    def new_id(cls):
        return ObjectId()

    @classmethod
    def get_oid(cls, _id, allow_invalid=True):
        if cls.is_valid_oid(_id):
            return ObjectId(_id)

        return _id if allow_invalid else None

    def to_dict(self, include_defaults=True, deep=True, extras={}):
        d = copy.deepcopy(self.__dict__) if deep else copy.copy(self.__dict__)
        if include_defaults:
            for k, v in self.get_all_defaults():
                d.setdefault(k, v)

        d.update(extras)
        return d

    @classmethod
    def get_client(cls):
        return cls.__client__

    @classmethod
    def get_all_defaults(cls):
        return cls.get_class_attr("__default_values__", attr_type={})

    def _get_default(self, key):
        for kls in self.__class__.__mro__:
            if key in kls.__dict__.get("__default_values__", {}):
                return kls.__default_values__[key]

        return None

    def __getitem__(self, key):
        return self.__dict__.get(key, self._get_default(key))

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return "{}".format(self.__dict__)

    def __getattr__(self, key):
        """return default value instead of key error"""
        return self._get_default(key)

    @classmethod
    def get_collection(cls):
        return cls.__mongo__.db[cls.__dict__["__collection__"]]

    @classmethod
    def get_wrapped_coll(cls, kwargs):
        tzinfo = cls.get_tzinfo(**kwargs)
        kwargs.pop("timezone", None)
        return cls.wrap_coll_tzinfo(cls.get_collection(), tzinfo)

    @classmethod
    def is_unique(cls, fields=[], doc={}, id=None, dbdoc={}, *args, **kwargs):
        spec = cls.get_uniq_spec(fields, doc)
        if spec:
            if id:
                spec["_id"] = {"$ne": id}

            kwargs.setdefault("as_raw", True)
            found_doc = cls.find_one(spec, *args, **kwargs)
            if found_doc:
                dbdoc.update(found_doc)
                return False

            return True

        return True

    @classmethod
    def get_tzinfo(cls, **kwargs):
        timezone = current_app.config.get("TIMEZONE")
        if not timezone:
            timezone = cls.__timezone__

        if timezone:
            if isinstance(timezone, str):
                return pytz.timezone(timezone)

            return timezone

        return None

    @classmethod
    def wrap_coll_tzinfo(cls, coll, tzinfo=None):
        if tzinfo:
            return coll.with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=tzinfo)
            )

        return coll

    @classmethod
    def get_page_args(cls, page_name=None, per_page_name=None, **kwargs):
        if not (page_name and per_page_name):
            return 0, 0, 0

        page = kwargs.get(page_name)
        per_page = kwargs.get(per_page_name)
        if not page:
            page = request.args.get(page_name, 1, type=int)

        if not per_page:
            per_page = request.args.get(per_page_name, 10, type=int)

        if not (page and per_page):
            return 0, 0, 0

        page = int(page)
        per_page = int(per_page)
        return page, per_page, per_page * (page - 1)

    @classmethod
    def _parse_find_options(cls, kwargs):
        paginate = kwargs.pop("paginate", False)
        page_name = kwargs.pop("page_name", None)
        per_page_name = kwargs.pop("per_page_name", None)
        page = per_page = skip = None
        if paginate and cls.__paginatecls__:
            page_name = page_name or "page"
            per_page_name = per_page_name or "per_page"

            page, per_page, skip = cls.__paginatecls__.get_page_args(
                page_name, per_page_name
            )

        if per_page:
            kwargs.setdefault("limit", per_page)

        if skip:
            kwargs.setdefault("skip", skip)

        kwargs.pop(page_name, None)
        kwargs.pop(per_page_name, None)
        kwargs.update(sort=get_sort(kwargs.get("sort")))

    def save(self, *args, **kwargs):
        """not pymongo save() method"""
        if self.id:
            return self.__class__.update_one(
                dict(_id=self.id), *args, **kwargs
            )

        return self.__class__.insert_one(self.to_dict(), **kwargs)

    def destroy(self, **kwargs):
        return self.__class__.delete_one(dict(_id=self.id), **kwargs)

    @classmethod
    def parse_indexes(cls, indexes=[]):
        """only used for create_indexes"""

        indexes_ = []
        for item in indexes or cls.__dict__.get("__indexes__", []):
            if isinstance(item, str):
                indexes_.append(IndexModel(get_sort(item, for_index=True)))
            else:
                indexes_.append(
                    IndexModel(get_sort(item[0], for_index=True), **item[1])
                )

        return indexes_

    @classmethod
    def get_sort(cls, sort):
        return get_sort(sort)

    @classmethod
    def get_uniq_spec(cls, fields=[], doc={}):
        return get_uniq_spec(
            fields or cls.__dict__.get("__unique_fields__", []), doc
        )

    @classmethod
    def get_class_attr(cls, name, include_parents=True, attr_type="list"):
        data = [] if attr_type == "list" else {}
        for kls in cls.__mro__:
            if name in kls.__dict__:
                if attr_type == "list":
                    data.extend(kls.__dict__[name])
                else:
                    for k, v in kls.__dict__[name].items():
                        data.setdefault(k, v)

            if not include_parents:
                break

        return data

    @classmethod
    def with_session(cls, action, *args, **kwargs):
        if cls.__use_transaction__ and cls.__support_transaction__:
            with cls.get_client().start_session() as sess:
                kwargs.setdefault("session", sess)
                with sess.start_transaction():
                    return action(*args, **kwargs)

        return action(*args, **kwargs)

    def clean_for_dirty(self, doc={}, keys=[]):
        """Remove non-changed items."""
        dct = self.__dict__.copy()
        for k in keys or list(doc.keys()):
            if k == "_id":
                return

            if k in doc and k in dct and doc[k] == dct[k]:
                doc.pop(k)


class BaseModel(BaseMixin):
    __collection__ = None
    __unique_fields__ = []  # not inherit
    __mongo__ = None  # flask-pymongo instance
    __client__ = None  # The MongoClient connected to the MongoDB server.
    __paginatecls__ = None  # for pagination
    __timezone__ = None
    __default_values__ = {}  # default value for non-exist fields
    # use IndexModel to create indexes
    # (see pymongo.operations.IndexModel for details)
    # __indexes__ item has 2 formats:
    # 1. key
    # 2. (key, IndexModel options)
    # format: [(key1, options), key2, key3, (keys4, options)]
    __indexes__ = []  # not inherit
    __background_index__ = None
    __support_transaction__ = False
    __use_transaction__ = False

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def find(cls, *args, **kwargs):
        # convert to object or keep dict format
        as_raw = kwargs.pop("as_raw", False)
        cls._parse_find_options(kwargs)
        cur = cls.with_session(
            cls.get_wrapped_coll(kwargs).find, *args, **kwargs
        )
        if as_raw:
            cur.objects = [doc for doc in cur]
        else:
            cur.objects = [cls(**doc) for doc in cur]

        return cur

    @classmethod
    def find_raw_batches(cls, *args, **kwargs):
        kwargs.pop("as_raw", None)
        cls._parse_find_options(kwargs)
        return cls.get_wrapped_coll(kwargs).find_raw_batches(*args, **kwargs)

    @classmethod
    def find_one(cls, filter=None, *args, **kwargs):
        if isinstance(filter, (str, ObjectId)):
            filter = dict(_id=cls.get_oid(filter))

        as_raw = kwargs.pop("as_raw", False)
        doc = cls.with_session(
            cls.get_wrapped_coll(kwargs).find_one, filter, *args, **kwargs
        )
        return (doc if as_raw else cls(**doc)) if doc else None

    @classmethod
    def find_one_and_delete(cls, *args, **kwargs):
        kwargs.update(sort=get_sort(kwargs.pop("sort", None)))
        return cls.with_session(
            cls.get_collection().find_one_and_delete, *args, **kwargs
        )

    @classmethod
    def find_one_and_replace(cls, *args, **kwargs):
        kwargs.update(sort=get_sort(kwargs.pop("sort", None)))
        return cls.with_session(
            cls.get_collection().find_one_and_replace, *args, **kwargs
        )

    @classmethod
    def find_one_and_update(cls, *args, **kwargs):
        kwargs.update(sort=get_sort(kwargs.pop("sort", None)))
        return cls.with_session(
            cls.get_collection().find_one_and_update, *args, **kwargs
        )

    @classmethod
    def insert_one(cls, doc, **kwargs):
        return cls.with_session(cls.get_collection().insert_one, doc, **kwargs)

    @classmethod
    def insert_many(cls, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().insert_many, *args, **kwargs
        )

    @classmethod
    def update_one(cls, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().update_one, *args, **kwargs
        )

    @classmethod
    def update_many(cls, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().update_many, *args, **kwargs
        )

    @classmethod
    def replace_one(cls, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().replace_one, *args, **kwargs
        )

    @classmethod
    def delete_one(cls, filter, **kwargs):
        return cls.with_session(
            cls.get_collection().delete_one, filter, **kwargs
        )

    @classmethod
    def delete_many(cls, filter, **kwargs):
        return cls.with_session(
            cls.get_collection().delete_many, filter, **kwargs
        )

    @classmethod
    def aggregate(cls, pipeline, **kwargs):
        docs = []
        for doc in cls.with_session(
            cls.get_collection().aggregate, pipeline, **kwargs
        ):
            docs.append(doc)

        return docs

    @classmethod
    def aggregate_raw_batches(cls, pipeline, **kwargs):
        return cls.get_collection().aggregate_raw_batches(pipeline, **kwargs)

    @classmethod
    def bulk_write(cls, requests, **kwargs):
        return cls.with_session(
            cls.get_collection().bulk_write, requests, **kwargs
        )

    @classmethod
    def create_index(cls, keys, **kwargs):
        keys = get_sort(keys, for_index=True)
        if cls.__background_index__ is not None:
            kwargs.setdefault("background", cls.__background_index__)

        coll = cls.get_collection()
        if keys and isinstance(keys, list):
            if isinstance(keys[0], list):  # [[(...), (...)], [(...)]]
                for key in keys:
                    cls.with_session(coll.create_index, key, **kwargs)

            else:  # [(), ()]
                cls.with_session(coll.create_index, keys, **kwargs)

    @classmethod
    def create_indexes(cls, indexes, **kwargs):
        if cls.__background_index__ is not None:
            kwargs.setdefault("background", cls.__background_index__)

        return cls.with_session(
            cls.get_collection().create_indexes,
            cls.parse_indexes(indexes),
            **kwargs
        )

    @classmethod
    def count_documents(cls, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().count_documents, *args, **kwargs
        )

    @classmethod
    def distinct(cls, key, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().distinct, key, *args, **kwargs
        )

    @classmethod
    def drop(cls, *args, **kwargs):
        return cls.with_session(cls.get_collection().drop)

    @classmethod
    def drop_index(cls, index_or_name, **kwargs):
        return cls.get_collection().drop_index(index_or_name, **kwargs)

    @classmethod
    def drop_indexes(cls, **kwargs):
        return cls.get_collection().drop_indexes(**kwargs)

    @classmethod
    def rename(cls, new_name, **kwargs):
        return cls.with_session(
            cls.get_collection().rename, new_name, **kwargs
        )

    @classmethod
    def index_information(cls):
        return cls.with_session(cls.get_collection().index_information)

    @classmethod
    def list_indexes(cls):
        return cls.with_session(cls.get_collection().list_indexes)

    @classmethod
    def map_reduce(cls, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().map_reduce, *args, **kwargs
        )

    @classmethod
    def inline_map_reduce(cls, *args, **kwargs):
        return cls.with_session(
            cls.get_collection().inline_map_reduce, *args, **kwargs
        )

    @classmethod
    def options(cls):
        return cls.with_session(cls.get_collection().options)

    @classmethod
    def reindex(cls):
        return cls.with_session(cls.get_collection().reindex)

    @classmethod
    def watch(cls, *args, **kwargs):
        return cls.with_session(cls.get_collection().watch, *args, **kwargs)

    @classmethod
    def with_options(cls, *args, **kwargs):
        return cls.get_collection().with_options(*args, **kwargs)

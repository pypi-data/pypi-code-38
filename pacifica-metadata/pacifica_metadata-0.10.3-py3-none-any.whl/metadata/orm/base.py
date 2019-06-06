#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Pacifica Metadata ORM Base Class.

This class implements the basic functionality needed for all
metadata objects in the metadata model for Pacifica.

PacificaModel.

Base class inherits from the PeeWee ORM Model class to create
required fields by all objects and serialization methods for
the base fields.

There are also CherryPy methods for creating, updating, getting
and deleting these objects in from a web service layer.
"""
import datetime
import uuid
from dateutil import parser
from peewee import Model, Expression, OP, AutoField, fn, CompositeKey, SQL, NodeList, BackrefAccessor
from six import text_type
from .utils import index_hash, ExtendDateTimeField
from .utils import datetime_converts, date_converts, datetime_now_nomicrosecond
from .globals import DB


def db_connection_decorator(func):
    """Wrap a method with a database connect and close."""
    def func_wrapper(*args, **kwargs):
        """Wrapper to connect and close connection to database."""
        if DB.is_closed():
            DB.connect()
        try:
            with DB.transaction():
                ret = func(*args, **kwargs)
        finally:
            DB.close()
        return ret
    return func_wrapper


class PacificaModel(Model):
    """
    Basic fields for an object within the model.

    Attributes:
        +-------------------+-------------------------------------+
        | Name              | Description                         |
        +===================+=====================================+
        | created           | When was the object created         |
        +-------------------+-------------------------------------+
        | updated           | When was the object last changed    |
        +-------------------+-------------------------------------+
        | deleted           | When was the object deleted         |
        +-------------------+-------------------------------------+
    """

    # this is peewee specific need to disable this check
    # pylint: disable=invalid-name
    id = AutoField()
    # pylint: enable=invalid-name
    created = ExtendDateTimeField(
        default=datetime_now_nomicrosecond, index=True)
    updated = ExtendDateTimeField(
        default=datetime_now_nomicrosecond, index=True)
    deleted = ExtendDateTimeField(null=True, index=True)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """PeeWee meta class contains the db connection."""

        database = DB
        only_save_dirty = True
    # pylint: enable=too-few-public-methods

    def _set_only_if(self, key, obj, dest_attr, func):
        if key in obj:
            setattr(self, dest_attr, func())

    def _set_only_if_by_name(self, attr, obj, cls):
        self._set_only_if(
            '{}_name'.format(attr), obj, attr,
            lambda: cls.get(cls.name == obj['{}_name'.format(attr)])
        )
        self._set_only_if(
            attr, obj, attr,
            lambda: cls.get(cls.uuid == uuid.UUID(obj[attr]))
        )

    def _set_date_part(self, date_part, obj):
        self._set_only_if(date_part, obj, date_part,
                          lambda: date_converts(obj[date_part]))

    def _set_datetime_part(self, time_part, obj):
        self._set_only_if(time_part, obj, time_part,
                          lambda: datetime_converts(obj[time_part]))

    @classmethod
    def cls_foreignkeys(cls):
        """Provide the foreign keys of the class as a list of attrs."""
        # pylint: disable=no-member
        return [ref.name for ref in cls._meta.refs.keys()]
        # pylint: enable=no-member

    @classmethod
    def cls_foreignkey_rel_mods(cls):
        """Return a collection of related models for a given foreignkey."""
        # pylint: disable=no-member
        return {fk.rel_model: fk.name for fk in cls._meta.refs}
        # pylint: enable=no-member

    @classmethod
    def cls_revforeignkeys(cls):
        """Provide the rev foreign keys of the class as a list of attrs."""
        ret = []
        for attr, value in cls.__dict__.items():
            if isinstance(value, BackrefAccessor):
                ret.append(attr)
        return ret

    def to_hash(self, **flags):
        """Convert the base object fields into serializable attributes in a hash."""
        recursion_depth = flags.get('recursion_depth', 0)
        recursion_limit = flags.get('recursion_limit', 1000)
        obj = {}
        obj['created'] = self.created.isoformat()
        obj['updated'] = self.updated.isoformat()
        obj['deleted'] = self.deleted.isoformat(
        ) if self.deleted is not None else None
        obj['_id'] = index_hash(obj['created'], obj['updated'], obj['deleted'])
        if recursion_depth:
            for attr in set(self.cls_revforeignkeys()) - set(flags.get('recursion_exclude', [])):
                list_count = getattr(self, attr).count()
                if list_count > recursion_limit:
                    obj[attr] = None
                elif list_count == 0:
                    obj[attr] = []
                else:
                    obj.update(self._build_object(attr))
        return obj

    def _build_object(self, attr):
        obj = {attr: []}
        fk_obj_list = {}
        for obj_ref in getattr(self, attr):
            if not fk_obj_list:
                fk_item_name, fk_obj_list = self._generate_fk_obj_list(obj_ref)
            append_item = self.get_append_item(
                obj_ref, fk_item_name, fk_obj_list)
            if append_item is not None:
                obj[attr].append(append_item)
        return obj

    @staticmethod
    def get_append_item(obj_ref, fk_item_name, fk_obj_list):
        """Generate the proper item to append to the newly built object."""
        if 'key' in fk_obj_list.values() and 'value' in fk_obj_list.values():
            append_item = {
                'key_id': obj_ref.__data__['key'],
                'value_id': obj_ref.__data__['value']
            }
        else:
            append_item = obj_ref.__data__[
                fk_item_name] if fk_item_name in obj_ref.__data__ else None
        # pylint: enable=protected-access
        return append_item

    def _generate_fk_obj_list(self, obj_ref):
        fk_obj_list = obj_ref.cls_foreignkey_rel_mods()
        valid_fk_obj_list = list(
            set(fk_obj_list) - set([self.__class__]))
        # pylint: disable=protected-access
        if len(valid_fk_obj_list) == 1:
            fk_item_name = fk_obj_list[valid_fk_obj_list.pop()]
        else:
            fk_item_name = obj_ref.__class__._meta.__dict__[
                'primary_key'].__dict__['column_name']
        # pylint: enable=protected-access
        return fk_item_name, fk_obj_list

    def from_hash(self, obj):
        """Convert the hash objects into object fields if they are present."""
        self._set_datetime_part('created', obj)
        self._set_datetime_part('updated', obj)
        self._set_datetime_part('deleted', obj)

    @staticmethod
    def _bool_translate(thing):
        """Translate the thing into a boolean."""
        return False if str(thing).lower() == 'false' else bool(thing)

    @staticmethod
    def _date_operator_compare(date, kwargs, dt_converts=datetime_converts):
        if '{0}_operator'.format(date) in kwargs:
            date_oper = getattr(
                OP, kwargs['{0}_operator'.format(date)].upper())
        else:
            date_oper = OP.EQ
        if date_oper == OP.BETWEEN:
            date_obj_min = dt_converts(kwargs['{}_0'.format(date)])
            date_obj_max = dt_converts(kwargs['{}_1'.format(date)])
            date_obj = NodeList((date_obj_min, SQL('AND'), date_obj_max))
        else:
            date_obj = dt_converts(kwargs[date])
        return (date_obj, date_oper)

    @classmethod
    def where_clause(cls, kwargs):
        """PeeWee specific extension meant to be passed to a PeeWee get or select."""
        where_clause = Expression(1, OP.EQ, 1)
        if 'deleted' in kwargs:
            if kwargs['deleted'] is None:
                where_clause &= Expression(
                    getattr(cls, 'deleted'), OP.IS, None)
            else:
                date_obj = datetime_converts(kwargs['deleted'])
                where_clause &= Expression(
                    getattr(cls, 'deleted'), OP.EQ, date_obj)
        for date in ['updated', 'created']:
            if date in kwargs:
                date_obj, date_oper = cls._date_operator_compare(date, kwargs)
                where_clause &= Expression(
                    getattr(cls, date), date_oper, date_obj)
        return where_clause

    @classmethod
    def _where_attr_clause(cls, where_clause, kwargs, keys):
        """Grab keys and operators out of kwargs and return where clause."""
        if '_id' in kwargs:
            where_clause &= Expression(getattr(cls, 'id'), OP.EQ, kwargs['_id'])
        for key in keys:
            if key in kwargs or '{}_id'.format(key) in kwargs:
                value = kwargs.get(key, kwargs.get('{}_id'.format(key)))
                key_oper = getattr(OP, kwargs.get('{}_operator'.format(key), 'EQ').upper())
                where_clause &= Expression(getattr(cls, key), key_oper, value)
        return where_clause

    @classmethod
    def last_change_date(cls):
        """Find the last changed date for the object."""
        # pylint: disable=no-value-for-parameter
        last_change_date = cls.select(fn.Max(cls.updated)).scalar()
        # pylint: enable=no-value-for-parameter
        last_change_string = last_change_date \
            if last_change_date is not None else '1970-01-01 00:00:00'
        last_change_string = last_change_date.isoformat(' ') \
            if isinstance(last_change_date, datetime.datetime) else parser.parse(last_change_string).isoformat(' ')
        return text_type(last_change_string)

    @classmethod
    def available_hash_list(cls):
        """
        Generate a hashable structure of all keys and values of keys.

        This structure allows for easy evaluation of updates or current vs old data
        for any object in the database.
        """
        hash_list = []
        hash_dict = {}
        all_keys_query = cls.select(*[getattr(cls, key)
                                      for key in cls.get_primary_keys()]).dicts()
        # pylint: disable=no-value-for-parameter
        for obj in all_keys_query.execute():
            # pylint: enable=no-value-for-parameter
            inst_key = index_hash(*obj.values())
            hash_list.append(inst_key)
            if 'uuid' in obj:
                obj['uuid'] = str(obj['uuid'])
            entry = {
                'key_list': obj,
                'index_hash': inst_key
            }
            hash_dict[inst_key] = entry
        return hash_list, hash_dict

    @classmethod
    def get_primary_keys(cls):
        """Return the primary keys for the object."""
        # pylint: disable=no-member
        primary_key = cls._meta.primary_key
        if isinstance(primary_key, CompositeKey) and cls._meta.refs:
            return list(primary_key.field_names)
        # pylint: enable=no-member
        return [primary_key.name]

    @classmethod
    def get_object_info(cls, where_clause=None):
        """Get model and field information about the model class."""
        related_model_info = {}
        # pylint: disable=no-member
        for fkf in cls._meta.refs:
            rel_mod = fkf.rel_model
            if rel_mod.__class__.__name__ != cls.__name__:
                # pylint: disable=protected-access
                table = rel_mod._meta.table_name
                pkey = rel_mod._meta.primary_key.name
                # pylint: enable=protected-access
                related_model_info[fkf.name] = {
                    'db_column': fkf.column_name,
                    'db_table': table,
                    'primary_key': pkey
                }
        where_clause = where_clause if where_clause else {}
        # pylint: disable=no-value-for-parameter
        field_types = {}
        for field_name, field in cls._meta.fields.items():
            field_types[field_name] = str(field.field_type)
        js_object = {
            'callable_name': cls.__module__.split('.').pop().lower(),
            'last_changed_date': cls.last_change_date(),
            'primary_keys': cls.get_primary_keys(),
            'field_list': cls._meta.sorted_field_names,
            'field_types': field_types,
            'foreign_keys': cls.cls_foreignkeys(),
            'related_models': related_model_info,
            'related_names': cls.cls_revforeignkeys(),
            'record_count': cls.select().where(cls.where_clause(where_clause)).count()
        }
        # pylint: enable=no-value-for-parameter
        # pylint: enable=no-member
        return js_object

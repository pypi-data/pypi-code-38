# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   sab 02 gen 2016 16:16:52 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2019 Lele Gaifax
#

from __future__ import unicode_literals

import sys
from logging import getLogger

from sqlalchemy import inspect
from sqlalchemy.orm import object_mapper, RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.exc import MultipleResultsFound

if sys.version_info.major >= 3:
    from itertools import zip_longest
else:
    from itertools import izip_longest as zip_longest

from . import File, SQL


logger = getLogger(__name__)

if sys.version_info.major >= 3:
    basestring = str


class Entity(object):
    """Model instances factory."""

    def __init__(self, model, key, fields=None, data=None, delete=False, loadonly=False):
        """Initialize a new factory.

        :type model: string
        :param model: the dotted full name of a mapped class
        :type key: either a string or a sequence of strings
        :param key: name(s) of the field(s) used to lookup existing instance
        :type fields: either None, a single string or a sequence of strings
        :param fields: if given, a list of field names
        :type data: either a single mapping or a list
        :param data: values used to initialize/update instances
        :type delete: boolean
        :param delete: if ``True``, existing instances will be deleted
        :type loadonly: boolean
        :param loadonly: if ``True``, perform only the search phase, don't update anything
        """
        self.model = model
        if isinstance(key, basestring):
            key = [key]
        self.key = key
        if isinstance(fields, basestring):
            fields = [fields]
        self.fields = fields
        if isinstance(data, dict):
            data = [data]
        self.data = data
        self.delete = delete
        self.loadonly = loadonly

    def __repr__(self):
        return "%s(model=%r, key=%r)" % (
            self.__class__.__name__,
            self.model, self.key)

    def __call__(self, session, idmap, adaptor=None):
        """Load, create or update a sequence of instances.

        :param adaptor: either None or a callable
        :rtype: an iterator over loaded/created/referenced instances
        """

        instances = self.data
        if instances is None:
            return

        for data in instances:
            instance = Instance(self, data, self.fields, idmap, adaptor)
            if self.loadonly:
                for i in instance(session, self.delete, self.loadonly):
                    yield i
            else:
                yield instance(session, self.delete, self.loadonly)


class Instance(object):
    """A single model instance."""

    def __init__(self, entity, data, fields, idmap, adaptor):
        self.entity = entity
        self.data = data
        self.fields = fields
        self.idmap = idmap
        self.adaptor = adaptor
        self.instance = None
        self.created = False

    def __call__(self, session, delete=False, loadonly=False):
        "Load an existing instance, create a new one or delete it if it exists"

        if self.instance is not None:
            return self.instance

        model = self.entity.model
        key = self.entity.key

        data = self.data
        if (self.fields is not None and isinstance(data, list)
            and len(self.fields) == len(data)):
            data = {f: v for f, v in zip(self.fields, data)}

        if self.adaptor is not None:
            data = self.adaptor(self.entity.model, self.entity.key, data)

        def getvalue(key):
            value = data.get(key, None)
            if isinstance(value, SQL):
                value = value.fetch(session)
            return self.idmap.get(id(value), value)

        filter = []
        for fname in key:
            if '->' in fname:
                attrname, _, slot = fname.partition('->')
                fvalue = getvalue(attrname)[slot]
            else:
                attrname = fname
                slot = None
                fvalue = getvalue(fname)

            if (sys.version_info.major < 3
                and isinstance(fvalue, basestring)
                and not isinstance(fvalue, unicode)):
                fvalue = fvalue.decode('utf-8')

            attr = getattr(model, attrname)
            has_custom_comparator = not isinstance(attr, InstrumentedAttribute)
            is_our_instance = isinstance(fvalue, Instance)
            if has_custom_comparator or not is_our_instance:
                if slot is not None:
                    attr = attr[slot]
                if is_our_instance:
                    filter.append(attr == fvalue(session))
                else:
                    filter.append(attr == fvalue)
            else:
                instance = fvalue(session)

                mapper = object_mapper(instance)
                pkeyf = mapper.primary_key
                pkeyv = mapper.primary_key_from_instance(instance)
                pkey = {f.name: v for f, v in zip_longest(pkeyf, pkeyv)}

                for l, r in attr.property.local_remote_pairs:
                    filter.append(getattr(model, l.name) == pkey[r.name])

        q = session.query(model)
        q = q.filter(*filter)

        if loadonly:
            return q

        try:
            obj = q.one_or_none()
        except MultipleResultsFound:
            logger.critical("Multiple instances found for %r with data %r filtered by %r",
                            model, data, ' AND '.join(str(f) for f in filter))
            raise

        if delete:
            if obj is not None:
                session.delete(obj)
            return obj

        if obj is None:
            # Create a new one
            obj = model()
            session.add(obj)
            self.created = True

        self.idmap[id(self.data)] = self
        self.instance = obj

        # Update it
        for f, v in data.items():
            try:
                attr_prop = getattr(model, f).property
            except AttributeError:
                attr_prop = None
            # If the attribute is a relationship or a traditional property (assuming its a
            # "generic foreign key") then assign the instance, otherwise its primary key
            assign_pk = not (attr_prop is None or isinstance(attr_prop, RelationshipProperty))
            try:
                setattr(obj, f, _get_value(session, self.idmap, assign_pk, f, v))
            except Exception:
                logger.critical("Could not assign value %r to attribute %r of %r",
                                v, f, obj)
                raise

        return obj


def _get_value(session, idmap, primary_key_only, attribute, value):
    # Extract the value to be assigned: if it is a dictionary or a list, then build a copy
    # recursively taking only the primary keys of the contained instances

    value = idmap.get(id(value), value)

    if isinstance(value, Instance):
        value = value(session)
        if primary_key_only:
            if inspect(value).pending:
                session.flush()
            mapper = object_mapper(value)
            pkeyv = mapper.primary_key_from_instance(value)
            if len(pkeyv) != 1:
                raise NotImplementedError('Unable to deal with multi column PK'
                                          ' assigning %r to "%s"' % (value, attribute))
            value = pkeyv[0]
    elif isinstance(value, File):
        value = value.read()
    elif isinstance(value, SQL):
        value = value.fetch(session)
    elif isinstance(value, dict):
        value = dict((k, _get_value(session, idmap, True, attribute, value[k])) for k in value)
    elif isinstance(value, list):
        value = [_get_value(session, idmap, True, attribute, v) for v in value]

    return value

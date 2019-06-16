# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Core Data Models
"""

from __future__ import unicode_literals, absolute_import

import re

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

from rattail.core import Object
from rattail.time import make_utc

# These are imported because most sibling modules import them *from* here (if
# that makes sense).  Probably need to think harder about the "best" place for
# these things to live.
from rattail.db.core import uuid_column, getset_factory
from rattail.db.types import GPCType


class ModelBase(Object):
    """
    Base class for all data models.
    """

    def __repr__(self):
        mapper = orm.object_mapper(self)

        key_props = []
        for prop in mapper.column_attrs:
            primary = True
            for column in prop.columns:
                if column not in mapper.primary_key:
                    primary = False
                    break
            if primary:
                key_props.append(prop)

        keys = ['{}={}'.format(prop.key, repr(getattr(self, prop.key)))
                for prop in key_props]

        return "{0}({1})".format(self.__class__.__name__, ', '.join(keys))

    @classmethod
    def get_model_title(cls):
        """
        Return a "humanized" version of the model name, for display in templates etc.
        """
        if hasattr(cls, 'model_title'):
            return cls.model_title
        # convert "CamelCase" to "Camel Case"
        return re.sub(r'([a-z])([A-Z])', r'\g<1> \g<2>', cls.__name__)

    @classmethod
    def get_model_title_plural(cls):
        """
        Return a "humanized" version of the plural model name, for display in templates etc.
        """
        if hasattr(cls, 'model_title_plural'):
            return cls.model_title_plural
        return '{}s'.format(cls.get_model_title())

    @classmethod
    def make_proxy(cls, main_class, extension, name):
        setattr(main_class, name, association_proxy(extension, name,
                                                    creator=lambda value: cls(**{name: value}),
                                                    getset_factory=getset_factory))


Base = declarative_base(cls=ModelBase)


@six.python_2_unicode_compatible
class Setting(Base):
    """
    Represents a "raw" config setting stored within the database.
    """
    __tablename__ = 'setting'

    name = sa.Column(sa.String(length=255), primary_key=True)
    value = sa.Column(sa.Text())

    def __str__(self):
        return self.name or ''


class Change(Base):
    """
    Represents a changed (or deleted) record, which is pending synchronization
    to another database.
    """
    __tablename__ = 'change'

    uuid = uuid_column()

    class_name = sa.Column(sa.String(length=40), nullable=False)

    # TODO: this needs to be renamed to e.g. object_key?  now that we sometimes
    # need to (mis)use it for non-UUID keys
    instance_uuid = sa.Column(sa.String(length=255), nullable=False, doc="""
    Key for the object which was changed/etc.  In most cases this will simply
    be the object's UUID value, hence the column name.  However in some cases
    it may contain something else; this is often needed in order to properly
    sync deletions to non-rattail systems, where the UUID is meaningless.
    """)

    object_key = orm.synonym('instance_uuid', doc="""
    Synonym to the :attr:`instance_uuid` column.  New code should perhaps
    reference the attribute by this (``object_key``) name instead, as the
    ``instance_uuid`` column may be renamed at some point, to this name.
    """)

    deleted = sa.Column(sa.Boolean(), nullable=False)

    def __repr__(self):
        return "Change(class_name={}, instance_uuid={}, deleted={})".format(
            repr(self.class_name), repr(self.instance_uuid), repr(self.deleted))


class Note(Base):
    """
    Arbitrary note attached to a supported object.
    """
    __tablename__ = 'note'
    __table_args__ = (
        sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='note_fk_created_by'),
    )
    __versioned__= {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    type = sa.Column(sa.String(length=15))
    subject = sa.Column(sa.String(length=255), nullable=True)
    text = sa.Column(sa.Text(), nullable=False)
    created = sa.Column(sa.DateTime(), nullable=False, default=make_utc)

    created_by_uuid = sa.Column(sa.String(length=32), nullable=False)
    created_by = orm.relationship('User')

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __str__(self):
        return str(self.text)

    if six.PY2:
        def __unicode__(self):
            return unicode(self.text)

#
# Copyright (c) 2019 UCT Prague.
# 
# models.py is part of Invenio Explicit ACLs 
# (see https://github.com/oarepo/invenio-explicit-acls).
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""A module implementing base ACL classes."""
import json
import os
import uuid
from abc import abstractmethod
from typing import Dict, Iterable, Union

import elasticsearch
from elasticsearch_dsl import Q
from flask_security import AnonymousUser
from invenio_accounts.models import User
from invenio_db import db
from invenio_records import Record
from invenio_search import current_search_client
from sqlalchemy import func
from sqlalchemy.util import classproperty
from sqlalchemy_utils import Timestamp

from invenio_explicit_acls.utils import schema_to_index

try:
    from psycopg2 import apilevel
    from sqlalchemy.dialects.postgresql import ARRAY

    StringArray = ARRAY(db.String)
except ImportError:
    # array represented in String field
    from .utils import ArrayType as ARRAY

    StringArray = ARRAY(db.String(length=1024))


def gen_uuid_key():
    return str(uuid.uuid4())


class ACL(db.Model, Timestamp):
    """
    An abstract class for ACLs.

    It defines:

    1. The priority of the ACL.
       Only the ACLs with the highest priority are taken into account when record ACLs are created
    2. The schemas for the resources that are handled by the ACL
    3. Operation that the ACL handles. It might be any string, to use helpers in
       the invenio_explicit_acls.permissions.py the operation needs to be one of 'get', 'update', 'delete'

    Subclasses of this class define the selection process which Records are handled by the given ACL - for example,
    "only the record with the given UUID", "all records in the schema", "records whose metadata in elasticsearch
    are matched by ES query" etc.
    """

    __tablename__ = 'explicit_acls_acl'

    id = db.Column(
        db.String(36),
        default=gen_uuid_key,
        primary_key=True
    )
    """Primary key."""

    name = db.Column(
        db.String(64),
        nullable=False
    )
    """Human readable name/description"""

    priority = db.Column(
        db.Integer,
        default=0)
    """Priority of the acl rule. Only the applicable rules with the highest priority get applied to the resource"""

    schemas = db.Column(StringArray)
    """
    Set of record schemas that this ACL handles. 
    
    Note that the schemas must be relative, for example records/record-v1.0.0.json.
    """

    originator_id = db.Column(db.ForeignKey(User.id, ondelete='CASCADE', ),
                              nullable=False, index=True)
    originator = db.relationship(
        User,
        backref=db.backref("authored_acls"))
    """The originator (person that last time modified the ACL)"""

    type = db.Column(db.String(50))
    """Type for polymorphism"""

    operation = db.Column(db.String(50))
    """An operation that actors can make"""

    actors = db.relationship("Actor", back_populates="acl")
    """A set of actors for this ACL (who have rights to perform an operation this ACL references)"""

    __mapper_args__ = {
        'polymorphic_identity': 'acl',
        'polymorphic_on': type
    }

    @classmethod
    @abstractmethod
    def get_record_acls(clz, record: Record) -> Iterable['ACL']:
        """
        Returns a list of ACL objects applicable for the given record.

        :param record: Invenio record
        """
        raise NotImplementedError('Must be implemented')

    @classmethod
    @abstractmethod
    def prepare_schema_acls(self, schema):
        """
        Prepare ACLs for the given index.

        :param schema: schema for which to prepare the ACLs
        """
        raise NotImplementedError('Must be implemented')

    @abstractmethod
    def get_matching_resources(self) -> Iterable[str]:
        """
        Get resources that match the ACL.

        :return:   iterable of resource ids
        """
        raise NotImplementedError('Must be implemented')

    @abstractmethod
    def update(self):
        """Update any internal representation / index for the acl."""
        raise NotImplementedError('Must be implemented')

    @abstractmethod
    def delete(self):
        """If the ACL writes itself to any other representation (such as ES index), delete it from there."""
        raise NotImplementedError('Must be implemented')

    @classmethod
    def enabled_schemas(clz) -> Iterable[str]:
        """Returns all schemas that have at least one ACL defined on them."""
        schemas = set()
        if db.engine.dialect.name == 'postgresql':
            # postgresql has array field, so return it from the array
            for acl_schemas in db.session.query(func.unnest(ACL.schemas)).distinct().all():
                schemas.update(acl_schemas)
        else:
            # otherwise iterate all the ACLs, let's hope there is not too many of them
            for acl in ACL.query.all():
                for schema in acl.schemas:
                    schemas.add(schema)
        return schemas

    def used_in_records(self, older_than_timestamp=None):
        """
        Returns IDs of all records that reference the ACL in cached acls in elasticsearch.

        :param older_than_timestamp:    only restrict to records where
                                        the cached ACLs are older than the timestamp
        :return:    An iterable of Record IDs
        """
        for schema in self.schemas:
            index, doc_type = schema_to_index(schema)

            query = [
                {
                    "term": {
                        "_invenio_explicit_acls.id": str(self.id)
                    }
                }
            ]

            if older_than_timestamp:
                query.append(
                    {
                        "range": {
                            "_invenio_explicit_acls.timestamp": {
                                "lt": older_than_timestamp
                            }
                        }
                    }
                )

            query = {
                "nested": {
                    "path": "_invenio_explicit_acls",
                    "score_mode": "min",
                    "query": {
                        "bool": {
                            "must": query
                        }
                    }
                }
            }

            for doc in elasticsearch.helpers.scan(
                current_search_client,
                query={
                    "query": query,
                    "_source": False,
                },
                index=index,
                doc_type=doc_type
            ):
                yield doc['_id']


class Actor(db.Model, Timestamp):
    """
    An abstract class for ACL actors.

    An Actor defines which users are given a permission to a record
    matched by ACL class.
    """

    __tablename__ = 'explicit_acls_actor'

    id = db.Column(
        db.String(36),
        default=gen_uuid_key,
        primary_key=True
    )

    name = db.Column(
        db.String(64)
    )

    type = db.Column(db.String(50))

    acl_id = db.Column(db.ForeignKey('explicit_acls_acl.id'))
    acl = db.relationship("ACL", back_populates="actors")

    originator_id = db.Column(db.ForeignKey(User.id, ondelete='CASCADE', ),
                              nullable=False, index=True)
    originator = db.relationship(
        User,
        backref=db.backref("authored_actors"))
    """The originator (person that last time modified the ACL)"""

    __mapper_args__ = {
        'polymorphic_identity': 'operation',
        'polymorphic_on': type
    }

    @classmethod
    @abstractmethod
    def get_elasticsearch_schema(clz, es_version):
        """
        Returns the elasticsearch schema for the _invenio_explicit_acls property.

        The property looks like::

            _invenio_explicit_acls [{
               "timestamp": "...when the ACL has been applied to the resource",
               "acl": <id of the acl>,
               "operation": name of the operation
               self.type: <the returned schema>
            }]

        :return:
        """
        raise NotImplementedError("Must be implemented")

    @abstractmethod
    def get_elasticsearch_representation(self, another=None, record=None, **kwargs):
        """
        Returns ES representation of this Actor.

        For a resource that matches ACL all the actors are serialized into _invenio_explicit_acls property::

            _invenio_explicit_acls [{
               "timestamp": "...when the ACL has been applied to the resource",
               "acl": <id of the acl>,
               "operation": name of the operation
               self.type: self.get_elasticsearch_representation()
            }]

        :param another: A serialized representation of the previous Actor of the same type.
                        The implementation should merge it with its own ES representation
        :return: The elasticsearch representation of the property on Record
        """
        raise NotImplementedError("Must be implemented")

    @classmethod
    @abstractmethod
    def get_elasticsearch_query(clz, user: Union[User, AnonymousUser], context: Dict) -> Q or None:
        """
        Returns elasticsearch query (elasticsearch_dls.Q) for the ACL.

        This is the counterpart of get_elasticsearch_representation and will be placed inside "nested" query
        _invenio_explicit_acls

        :param user:     the user to be checked
        :param context:  any extra context carrying information about the user
        :return:         elasticsearch query that enforces the user
        """
        raise NotImplementedError("Must be implemented")

    @abstractmethod
    def user_matches(self, user: Union[User, AnonymousUser], context: Dict, record: Record = None) -> bool:
        """
        Checks if a user is allowed to perform any operation according to the ACL.

        :param user: user being checked against the ACL
        :param context:  any extra context carrying information about the user
        """
        raise NotImplementedError('Must be implemented')

    @abstractmethod
    def get_matching_users(self, record: Record = None) -> Iterable[int]:
        """
        Returns a list of users matching this Actor.

        :return: Iterable of a user ids
        """
        raise NotImplementedError('Must be implemented')


__all__ = [
    'ACL',
    'Actor'
]

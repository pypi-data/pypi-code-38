#
# Copyright (c) 2019 UCT Prague.
# 
# api.py is part of Invenio Explicit ACLs 
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
"""Public API for explicit ACL module."""
import datetime
import json
import logging
import os
from typing import Iterable

from elasticsearch import VERSION as ES_VERSION
from flask import current_app
from invenio_db import db
from invenio_records import Record
from invenio_search import current_search_client
from werkzeug.utils import cached_property

from invenio_explicit_acls.tasks import acl_changed_reindex, \
    acl_deleted_reindex
from invenio_explicit_acls.utils import schema_to_index

from .models import ACL, Actor

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class AclAPI:
    """Implementation of public explicit ACL API."""

    def __init__(self, app):
        """
        API initialization.

        :param app: invenio application
        """
        self.app = app

    @property
    def actor_models(self):
        """
        Returns all db models inherited from Actor.

        :return list of Actor classes
        """
        return [
            cls for cls in db.Model._decl_class_registry.values()
            if isinstance(cls, type) and issubclass(cls, Actor) and cls is not Actor
        ]

    @property
    def acl_models(self):
        """
        Returns all db models inherited from ACL.

        :return list of ACL classes
        """
        return [
            cls for cls in db.Model._decl_class_registry.values()
            if isinstance(cls, type) and issubclass(cls, ACL) and cls is not ACL
        ]

    def prepare(self, schema):
        """
        Add ACL support for a given schema.

        This call goes through all registered ACL types
        and lets them do whatever preparation is needed (for example, creating extra indices
        in elasticsearch).

        Then it adds _invenio_explicit_acls field to the elasticsearch index for the given schema
        that wil store preprocessed explicit ACLs for each record

        :param schema:  schema URL of the schema that should be patched with ACL support
        """
        # let each acl model to prepare the schema if needed
        for model in self.acl_models:
            model.prepare_schema_acls(schema)

        # add an extra column containing preprocessed ACLs to the prepared schema
        index_name, doc_type = schema_to_index(schema)

        # print(json.dumps(self._extra_mapping, indent=4))
        current_search_client.indices.put_mapping(index=index_name, doc_type=doc_type, body=self._extra_mapping)

    @cached_property
    def _extra_mapping(self):
        """
        Returns a ES mapping.

        :return: dict that defines extra column that will be added to ES mapping
        """
        extra_mapping = os.path.join(os.path.dirname(__file__), 'mappings', 'mixins', 'v%s' % ES_VERSION[0],
                                     current_app.config['INVENIO_EXPLICIT_ACLS_MIXIN_NAME'] + '.json')
        with open(extra_mapping, 'r') as f:
            extra_mapping = json.load(f)

        actors = extra_mapping['properties']['_invenio_explicit_acls']['properties']

        for actor in self.actor_models:
            actor_type = actor.__mapper_args__['polymorphic_identity']
            actors[actor_type] = actor.get_elasticsearch_schema(ES_VERSION[0])
        return extra_mapping

    def get_record_acls(self, record: Record) -> Iterable[ACL]:
        """
        Returns a list of ACL objects applicable for the given record.

        :param record: Invenio record
        """
        applicable_acls = []
        for acl in self.acl_models:
            applicable_acls.extend(acl.get_record_acls(record))

        # return those applicable acls with the highest priority
        if applicable_acls:
            max_priority = max([x.priority for x in applicable_acls])
            return [x for x in applicable_acls if x.priority == max_priority]

        return []

    @property
    def acl_doctype_name(self):
        """Return doctype of index in which percolate ACL queries are stored."""
        return self.app.config['INVENIO_EXPLICIT_ACLS_DOCTYPE_NAME']

    @property
    def enabled_schemas(self):
        """Returns a set of schemas for which there exists at least one ACL."""
        return ACL.enabled_schemas()

    def serialize_record_acls(self, record_acls: Iterable[ACL], record=None):
        """
        Serializes a set of record ACLs to json form that will be attached to a record.

        :param record_acls: iterable of ACLs
        :return:            json with precompiled ACLs to be put as an extra property to elasticsearch
        """
        timestamp = datetime.datetime.now().astimezone().isoformat()

        acl_def = []

        for record_acl in record_acls:  # type: ACL
            actors = {}
            for actor in record_acl.actors:  # type: Actor
                actor_type = actor.__mapper_args__['polymorphic_identity']
                actors[actor_type] = actor.get_elasticsearch_representation(actors.get(actor_type, None), record=record)

            if actors:
                acl_def.append({
                    'operation': record_acl.operation,
                    'id': str(record_acl.id),
                    'timestamp': timestamp,
                    **actors
                })

        return acl_def

    def reindex_acl(self, acl: ACL, delayed=True):
        """
        Reindex resources when ACL is changed.

        :param acl:         the ACL that has been created/changed
        :param delayed:     if True and INVENIO_EXPLICIT_ACLS_DELAYED_REINDEX is True as well,
                            reindex in a background task in celery, otherwise reindex before the call returns
        """
        try:
            acl.update()
        except:  # pragma no cover
            logger.exception('Error: could not update ACL index')

        if delayed and current_app.config['INVENIO_EXPLICIT_ACLS_DELAYED_REINDEX']:
            acl_changed_reindex.delay(str(acl.id))              # pragma no cover
        else:
            acl_changed_reindex(str(acl.id))

    def reindex_acl_removed(self, acl: ACL, delayed=True):
        """
        Reindex resources when ACL is removed.

        :param acl:             the removed ACL (must not be present in database)
        :param delayed:         if True and INVENIO_EXPLICIT_ACLS_DELAYED_REINDEX is True as well,
                                reindex in a background task in celery, otherwise reindex before the call returns
        """
        try:
            acl.delete()
        except:  # pragma no cover
            logger.exception('Error: could not delete ACL index')

        if delayed and current_app.config['INVENIO_EXPLICIT_ACLS_DELAYED_REINDEX']:
            acl_deleted_reindex.delay(acl.schemas, str(acl.id))  # pragma no cover
        else:
            acl_deleted_reindex(acl.schemas, str(acl.id))


__all__ = ('AclAPI',)

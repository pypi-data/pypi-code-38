#
# Copyright (c) 2019 UCT Prague.
# 
# es_mixin.py is part of Invenio Explicit ACLs 
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
"""Mixin for ACLs that are implemented via ES query."""
import json
import logging
from typing import Iterable

import elasticsearch
from flask import current_app
from invenio_indexer import current_record_to_index
from invenio_records import Record
from invenio_search import current_search, current_search_client

from invenio_explicit_acls.models import ACL
from invenio_explicit_acls.proxies import current_explicit_acls
from invenio_explicit_acls.utils import schema_to_index

logger = logging.getLogger(__name__)


class ESACLMixin(object):
    """Mixin to be used with ACL class as a base for ES-based ACLs."""

    @property
    def record_selector(self):
        """Returns an elasticsearch query matching resources that this ACL maps to."""
        raise NotImplementedError("Implement this method")  # pragma no cover

    @classmethod
    def get_record_acls(clz, record: Record) -> Iterable['ACL']:
        """
        Returns a list of ACL objects applicable for the given record.

        :param record: Invenio record
        :return:
        """
        # run percolate query on the index record's index

        query = clz._get_percolate_query(record)
        if logger.isEnabledFor(logging.DEBUG) <= logging.DEBUG:
            logger.debug('get_material_acls: query %s', json.dumps(query, indent=4, ensure_ascii=False))
        index, _doc_type = current_record_to_index(record)
        try:
            for r in current_search_client.search(
                index=clz.get_acl_index_name(index),
                doc_type=current_app.config['INVENIO_EXPLICIT_ACLS_DOCTYPE_NAME'],
                body=query
            )['hits']['hits']:
                yield clz.query.get(r['_id'])
        except elasticsearch.TransportError as e:
            logger.error('Error running ACL query on index %s, doctype %s, query %s',
                         clz.get_acl_index_name(index), current_app.config['INVENIO_EXPLICIT_ACLS_DOCTYPE_NAME'],
                         query)
            if e.status_code == 404:
                raise RuntimeError('Explicit ACLs were not prepared for the given schema. '
                                   'Please run invenio explicit-acls prepare %s' % record.get('$schema', ''))
            else:  # pragma: no cover
                raise

    @classmethod
    def _get_percolate_query(cls, record):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "percolate": {
                                "field": "__acl_record_selector",
                                "document": dict(record)
                            }
                        },
                        {
                            "term": {
                                "__acl_record_type": cls.__mapper_args__['polymorphic_identity']
                            }
                        }
                    ]
                }
            }
        }
        return query

    @classmethod
    def prepare_schema_acls(self, schema):
        """
        Prepare ACLs for the given index.

        :param schema: schema for which to prepare the ACLs
        """
        index_name, doc_type = schema_to_index(schema)

        # create a new index where percolate queries will be stored
        acl_index_name = self.get_acl_index_name(index_name)
        # create mapping for acl index

        target_mapping_resource = current_search.mappings[index_name]
        with open(target_mapping_resource) as f:
            mapping = json.load(f)

        acl_doctype_name = current_explicit_acls.acl_doctype_name

        fk = next(iter(mapping['mappings'].keys()))
        mapping['mappings'][acl_doctype_name] = mapping['mappings'][fk]
        del mapping['mappings'][fk]

        mapping['mappings'][acl_doctype_name]['properties'] = {
            **mapping['mappings'][acl_doctype_name]['properties'],
            "__acl_record_selector": {
                "type": "percolator"
            },
            "__acl_record_type": {
                "type": "keyword"
            }
        }

        try:
            current_search_client.indices.create(index=acl_index_name, body=mapping)
        except Exception as e:
            logger.error('Error in creating index for ACLs: %s', e)

    def get_matching_resources(self) -> Iterable[str]:
        """
        Get resources that match the ACL.

        :param acl: the acl
        :return:   iterable of resource ids
        """
        for schema in self.schemas:
            index_name, doc_type = schema_to_index(schema)
            try:
                for doc in elasticsearch.helpers.scan(
                    current_search_client,
                    query={
                        "query": self.record_selector,
                        "_source": False,
                    },
                    index=index_name, doc_type=doc_type
                ):
                    yield doc['_id']
            except:  # pragma: no cover
                logger.exception('Error getting resources for schema %s', schema)

    def update(self):
        """Update any internal representation / index for the acl."""
        body = {
            '__acl_record_selector': self.record_selector,
            '__acl_record_type': self.type
        }
        if logger.isEnabledFor(logging.DEBUG) <= logging.DEBUG:
            logger.debug('get_material_acls: query %s', json.dumps(body, indent=4, ensure_ascii=False))
        schema_indices = [schema_to_index(x)[0] for x in self.schemas]
        acl_index_names = [self.get_acl_index_name(x) for x in schema_indices]
        for acl_idx_name in acl_index_names:
            try:
                resp = current_search_client.index(
                    index=acl_idx_name,
                    doc_type=current_app.config['INVENIO_EXPLICIT_ACLS_DOCTYPE_NAME'],
                    id=self.id,
                    body=body
                )
                assert resp['result'] in ('created', 'updated')
            finally:
                current_search_client.indices.flush(index=acl_idx_name)

    def delete(self):
        """Delete acl from any internal representation / index for the acl."""
        for schema in self.schemas:
            acl_index_name = self.get_acl_index_name(schema_to_index(schema)[0])
            try:
                return current_search_client.delete(
                    index=acl_index_name,
                    doc_type=current_app.config['INVENIO_EXPLICIT_ACLS_DOCTYPE_NAME'],
                    id=self.id
                )
            except:  # pragma: no cover
                logger.exception('Strange, the ACL has not been indexed: %s', repr(self))
            finally:
                current_search_client.indices.flush(index=acl_index_name)

    @classmethod
    def get_acl_index_name(clz, target_index_name):
        """
        Returns IDs of all records that reference the ACL in cached acls in elasticsearch.

        :param older_than_timestamp:    only restrict to records where
                                        the cached ACLs are older than the timestamp
        :return:    An iterable of Record IDs
        """
        return f'{current_app.config["INVENIO_EXPLICIT_ACLS_INDEX_NAME"]}-{target_index_name}'

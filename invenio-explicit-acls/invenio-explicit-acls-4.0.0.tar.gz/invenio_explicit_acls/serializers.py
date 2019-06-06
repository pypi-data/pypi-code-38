#
# Copyright (c) 2019 UCT Prague.
# 
# serializers.py is part of Invenio Explicit ACLs 
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
"""Defines serializer mixin that for each record returns cached ACLs in 'invenio_explicit_acls' property."""
import logging

from flask import current_app, has_request_context, request
from invenio_records_rest.serializers import JSONSerializer
from invenio_records_rest.serializers.base import PreprocessorMixin
from invenio_records_rest.utils import obj_or_import_string
from invenio_search import current_search
from invenio_search.utils import schema_to_index

from invenio_explicit_acls.acl_records_search import ACL_MATCHED_QUERY, \
    ACLRecordsSearch

logger = logging.getLogger(__name__)


class ACLSerializerMixin(PreprocessorMixin):
    """A mixin for invenio serializers to add ACLs to serialized record."""

    acl_rest_endpoint = None
    """endpoint key from RECORDS_REST_ENDPOINTS of the resource that this serializer is about to serialize."""

    acl_operations = ('get', 'update', 'delete')
    """
    set of acl operations that will be checked if user has access to them. 
    
    Requires that the search_class
    defined on the rest endpoint must be inherited from ACLRecordsSearch.
    """

    def __init__(self, *args, **kwargs):
        """Creates an instance."""
        self.acl_rest_endpoint = kwargs.pop('acl_rest_endpoint', type(self).acl_rest_endpoint)
        super().__init__(*args, **kwargs)

    def preprocess_record(self, pid, record, links_factory=None, **kwargs):
        """Adds cached ACLs to the serialized record."""
        ret = super().preprocess_record(pid, record, links_factory, **kwargs)

        index_names = current_search.mappings.keys()
        index, doc_type = schema_to_index(record['$schema'], index_names=index_names)

        search_class = None
        if self.acl_rest_endpoint is None:
            if has_request_context():
                search_class = getattr(request._methodview, 'search_class')
            if not search_class:  # pragma no cover
                raise AttributeError('Please set acl_rest_endpoint property with the key to RECORDS_REST_ENDPOINTS')
        else:
            rest_configuration = current_app.config['RECORDS_REST_ENDPOINTS'][self.acl_rest_endpoint]
            search_class = obj_or_import_string(rest_configuration.get('search_class', None), default=ACLRecordsSearch)

        sc = search_class(index=index, doc_type=doc_type)

        rec = sc.acl_return_all(operation=self.acl_operations).get_record(str(record.id))
        rec = rec.execute()

        if rec.hits:
            matched_acls = getattr(rec.hits[0].meta, 'matched_queries', [])
            matched_acls = [x.replace(f'{ACL_MATCHED_QUERY}_', '') for x in matched_acls]
        else:   # pragma no cover
            logger.error('Should not happen, record %s not found in elasticsearch', record.id)
            matched_acls = []

        ret['invenio_explicit_acls'] = matched_acls

        return ret

    @staticmethod
    def preprocess_search_hit(pid, record_hit, links_factory=None, **kwargs):
        """Prepare a record hit from Elasticsearch for serialization."""
        ret = PreprocessorMixin.preprocess_search_hit(pid, record_hit, links_factory=links_factory, **kwargs)
        matched_acls = record_hit.get('matched_queries', [])
        matched_acls = [x.replace(f'{ACL_MATCHED_QUERY}_', '') for x in matched_acls]
        ret['invenio_explicit_acls'] = matched_acls
        return ret


class ACLJSONSerializer(ACLSerializerMixin, JSONSerializer):
    """A JSON serializer that adds ACLs to the serialized record."""

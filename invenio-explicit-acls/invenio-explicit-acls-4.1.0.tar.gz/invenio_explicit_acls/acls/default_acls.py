#
# Copyright (c) 2019 UCT Prague.
# 
# default_acls.py is part of Invenio Explicit ACLs 
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
"""Models for storing Default ACLs."""
from typing import Iterable

from invenio_db import db
from invenio_records import Record
from invenio_search import current_search_client
from sqlalchemy import func

from invenio_explicit_acls.models import ACL
from invenio_explicit_acls.utils import get_record_acl_enabled_schema, \
    schema_to_index


class DefaultACL(ACL):
    """Storage for ACL Sets."""

    __tablename__ = 'explicit_acls_defaultacl'
    __mapper_args__ = {
        'polymorphic_identity': 'default',
    }

    id = db.Column(db.String(36), db.ForeignKey('explicit_acls_acl.id'), primary_key=True)
    """Id maps to base class' id"""

    def __repr__(self):
        """String representation for model."""
        return 'Default ACL on {0.schemas}'.format(self)

    @classmethod
    def get_record_acls(clz, record: Record) -> Iterable['ACL']:
        """
        Returns a list of ACL objects applicable for the given record.

        :param record: Invenio record
        """
        schema = get_record_acl_enabled_schema(record)
        if db.engine.dialect.name == 'postgresql':
            # postgresql has array field, so search in the array
            for r in DefaultACL.query.filter(DefaultACL.schemas.any(schema)).all():
                yield r
        else:
            # otherwise iterate all the default ACLs, let's hope there is not too many of them
            for acl in DefaultACL.query.all():
                if schema in acl.schemas:
                    yield acl

    @classmethod
    def prepare_schema_acls(self, schema):
        """
        Prepare ACLs for the given index.

        :param schema: schema for which to prepare the ACLs
        """
        # no need to prepare any index
        pass

    def get_matching_resources(self) -> Iterable[str]:
        """
        Get resources that match the ACL.

        :param acl: the acl
        :return:   iterable of resource ids
        """
        for schema in self.schemas:
            index, doc_type = schema_to_index(schema)

            for r in current_search_client.search(
                index=index,
                doc_type=doc_type,
                body={
                    "query": {
                        "match_all": {}
                    },
                    "_source": False,
                }
            )['hits']['hits']:
                yield r['_id']

    def update(self):
        """Update any internal representation / index for the acl."""
        # no need to update any index
        pass

    def delete(self):
        """Delete acl from any internal representation / index for the acl."""
        # no need to update any index
        pass

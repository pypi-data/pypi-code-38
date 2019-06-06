#
# Copyright (c) 2019 UCT Prague.
# 
# elasticsearch_acls.py is part of Invenio Explicit ACLs 
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
"""Models for storing Elasticsearch ACLs."""
import logging

from invenio_db import db

from invenio_explicit_acls.models import ACL

from .es_mixin import ESACLMixin

try:
    from psycopg2 import apilevel
    from sqlalchemy.dialects.postgresql import JSONB as JSON
except:
    from sqlalchemy.types import JSON

logger = logging.getLogger(__name__)


class ElasticsearchACL(ESACLMixin, ACL):
    """Storage for ACL Sets."""

    __tablename__ = 'explicit_acls_elasticsearchacl'
    __mapper_args__ = {
        'polymorphic_identity': 'elasticsearch',
    }

    #
    # Fields
    #
    id = db.Column(db.String(36), db.ForeignKey('explicit_acls_acl.id'), primary_key=True)
    """Id maps to base class' id"""

    record_selector = db.Column(JSON)
    """JSON field with pattern to which the ACL applies. 
        For example, {'faculty': 'FCHI'} pattern selects all resources with faculty FCHI
    """

    def __repr__(self):
        """String representation for model."""
        return '"{0.name}" ({0.id}) on schemas {0.schemas}'.format(self)


__all__ = ('ElasticsearchACL',)

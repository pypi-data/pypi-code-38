#
# Copyright (c) 2019 UCT Prague.
#
# user.py is part of Invenio Explicit ACLs
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
"""A modul that defines user actor."""
from typing import Dict, Union

from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Term
from flask_security import AnonymousUser
from invenio_accounts.models import User


class UserMixin:
    """An actor mixin for matching a set of users."""

    @classmethod
    def get_elasticsearch_schema(clz, _es_version):
        """
        Returns the elasticsearch schema for the _invenio_explicit_acls property.

        The property looks like::

            _invenio_explicit_acls [{
               "timestamp": "...when the ACL has been applied to the resource",
               "acl": <id of the acl>,
               "operation": name of the operation
                user: [1, 2, 3]
            }]

        :return:
        """
        return {
            'type': 'integer'
        }

    @classmethod
    def get_elasticsearch_query(clz, user: Union[User, AnonymousUser], context: Dict) -> Q or None:
        """
        Returns elasticsearch query (elasticsearch_dls.Q) for the ACL.

        This is the counterpart of get_elasticsearch_representation and will be placed inside "nested" query
        _invenio_explicit_acls

        :param user:  the user to be checked
        :param context:  any extra context carrying information about the user
        :return:      elasticsearch query that enforces the user
        """
        if user.is_authenticated:
            return Term(_invenio_explicit_acls__user=user.id)
        else:
            return None


class RoleMixin:
    """An actor mixin for matching a set of roles."""

    @classmethod
    def get_elasticsearch_schema(clz, _es_version):
        """
        Returns the elasticsearch schema for the _invenio_explicit_acls property.

        The property looks like::

            _invenio_explicit_acls [{
               "timestamp": "...when the ACL has been applied to the resource",
               "acl": <id of the acl>,
               "operation": name of the operation
               "role": [1,2]
            }]

        """
        return {
            'type': 'integer'
        }


    @classmethod
    def get_elasticsearch_query(clz, user: User, context: Dict) -> Q or None:
        """
        Returns elasticsearch query (elasticsearch_dls.Q) for the ACL.

        This is the counterpart of get_elasticsearch_representation and will be placed inside "nested" query
        _invenio_explicit_acls

        :param user:  the user to be checked
        :param context:  any extra context carrying information about the user
        :return:      elasticsearch query that enforces the user
        """
        if user.is_authenticated:
            return Q('terms', _invenio_explicit_acls__role=[x.id for x in user.roles])
        return None

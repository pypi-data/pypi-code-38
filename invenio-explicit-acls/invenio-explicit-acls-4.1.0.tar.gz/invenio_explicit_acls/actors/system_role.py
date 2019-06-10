#
# Copyright (c) 2019 UCT Prague.
# 
# system_role.py is part of Invenio Explicit ACLs 
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
"""A modul that defines anonymous actor."""
import logging
from typing import Dict, Iterable

from elasticsearch_dsl import Q
from flask import g
from invenio_accounts.models import User
from invenio_db import db
from invenio_records import Record

from ..models import Actor

logger = logging.getLogger(__name__)


class SystemRoleActor(Actor):
    """An actor matching authenticated users, anonymous users or everyone."""

    __tablename__ = 'explicit_acls_system_role'
    __mapper_args__ = {
        'polymorphic_identity': 'system_role',
    }

    id = db.Column(db.String(36), db.ForeignKey('explicit_acls_actor.id'), primary_key=True)
    """Id maps to base class' id"""

    system_role = db.Column(db.String(32))
    """The system role (any_user, authenticated_user)."""

    def __str__(self):
        """Returns the string representation of the actor."""
        return 'SystemRoleActor[%s]' % self.name

    @classmethod
    def get_elasticsearch_schema(clz, _es_version):
        """
        Returns the elasticsearch schema for the _invenio_explicit_acls property.

        The property looks like::

            _invenio_explicit_acls [{
               "timestamp": "...when the ACL has been applied to the resource",
               "acl": <id of the acl>,
               "operation": name of the operation
                system_role: ["any_user", "authenticated_user"]
            }]

        :return:
        """
        return {
            'type': 'keyword'
        }

    def get_elasticsearch_representation(self, another=None, record=None, **kwargs):
        """
        Returns ES representation of this Actor.

        :param another: A serialized representation of the previous Actor of the same type.
                        The implementation should merge it with its own ES representation
        :return: The elasticsearch representation of the property on Record
        """
        return [self.system_role] + (another or [])

    @classmethod
    def get_elasticsearch_query(clz, user: User, context: Dict) -> Q or None:
        """
        Returns elasticsearch query (elasticsearch_dls.Q) for the ACL.

        This is the counterpart of get_elasticsearch_representation and will be placed inside "nested" query

        If the user is not current_user you MUST provide 'system_roles' in context containing a collection of:

           * strings
           * invenio_access.permissions.SystemRoleNeed (such as any_user, authenticated_user)

        :param user:  the user to be checked
        :param context:  any extra context carrying information about the user.
        :return:      elasticsearch query that enforces the user
        """
        if user.is_anonymous:
            return Q('term', _invenio_explicit_acls__system_role='any_user')

        roles = clz._get_system_roles(context, user)

        return Q('terms', _invenio_explicit_acls__system_role=roles)

    @classmethod
    def _get_system_roles(cls, context, user):
        if 'system_roles' in context:
            roles = []
            for r in context['system_roles']:
                if isinstance(r, str):
                    roles.append(r)
                elif r[0] == 'system_role':
                    roles.append(r[1])
            roles = sorted(roles)
        else:
            if not hasattr(g, 'identity'):  # pragma: no cover
                raise AttributeError(
                    'Can not determine system role for a user that does not have Identity in flask.g. '
                    'Please add system_roles to context.')

            identity = g.identity
            if not identity:  # pragma: no cover
                raise AttributeError(
                    'Can not determine system role for a user that does not have Identity in flask.g. '
                    'Please add system_roles to context.')

            if identity.id != user.id:
                raise AttributeError(
                    'Can not determine system role for a user whose id does not match Identity in flask.g. '
                    f'Identity id is "{identity.id}", supplied user id "{user.id}".'
                    'Please add system_roles to context.')

            # sorting for easier tests
            roles = sorted([p[1] for p in identity.provides if p[0] == 'system_role'])
        return roles

    def user_matches(self, user: User, context: Dict, record: Record = None) -> bool:
        """
        Checks if a user is allowed to perform any operation according to the ACL.

        :param user: user being checked against the ACL
        :param context:  any extra context carrying information about the user
        """
        roles = self._get_system_roles(context, user)
        return self.system_role in roles

    def get_matching_users(self, record: Record = None) -> Iterable[int]:
        """
        Returns a list of users matching this Actor.

        :return: Iterable of a user ids
        """
        if self.system_role == 'any_user' or self.system_role == 'authenticated_user':
            for u in User.query.all():
                yield u.id
        else:
            raise NotImplementedError(
                'Can not get a list of matching users for system role %s - not implemented' % self.system_role)

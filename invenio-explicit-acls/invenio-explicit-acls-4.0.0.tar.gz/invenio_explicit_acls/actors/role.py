#
# Copyright (c) 2019 UCT Prague.
# 
# role.py is part of Invenio Explicit ACLs 
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
"""Actor matching invenio roles."""
from typing import Dict, Iterable

from elasticsearch_dsl import Q
from invenio_accounts.models import Role, User
from invenio_db import db
from invenio_records import Record

from invenio_explicit_acls.actors.mixins import RoleMixin

from ..models import Actor

roles_actors = db.Table('explicit_acls_roles_roleactors',
                        db.Column('role_id', db.Integer, db.ForeignKey('accounts_role.id'), primary_key=True),
                        db.Column('actor_id', db.String(36), db.ForeignKey('explicit_acls_roleactor.id',
                                                                           name='explicit_acls_ra1'),
                                  primary_key=True)
                        )


class RoleActor(RoleMixin, Actor):
    """An actor matching set of invenio roles."""

    __tablename__ = 'explicit_acls_roleactor'
    __mapper_args__ = {
        'polymorphic_identity': 'role',
    }

    id = db.Column(db.String(36), db.ForeignKey('explicit_acls_actor.id'), primary_key=True)
    """Id maps to base class' id"""

    roles = db.relationship(Role, secondary=roles_actors, lazy='subquery',
                            backref=db.backref('actors', lazy=True))

    def __str__(self):
        """Returns the string representation of the actor."""
        return 'RoleActor[%s]' % self.name

    def get_elasticsearch_representation(self, others=None, record=None, **kwargs):
        """
        Returns ES representation of this Actor.

        :param another: A serialized representation of the previous Actor of the same type.
                        The implementation should merge it with its own ES representation
        :return: The elasticsearch representation of the property on Record
        """
        return list(set([x.id for x in self.roles] + (others or [])))

    def user_matches(self, user: User, context: Dict, record: Record = None) -> bool:
        """
        Checks if a user is allowed to perform any operation according to the ACL.

        :param user: user being checked against the ACL
        :param context:  any extra context carrying information about the user
        """
        role_ids = set(x.id for x in self.roles)
        for role in user.roles:
            if role.id in role_ids:
                return True
        return False

    def get_matching_users(self, record: Record = None) -> Iterable[int]:
        """
        Returns a list of users matching this Actor.

        :return: Iterable of a user ids
        """
        ret = set()
        for r in self.roles:
            for u in r.users:
                ret.add(u.id)
        return ret

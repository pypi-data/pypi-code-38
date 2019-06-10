#
# Copyright (c) 2019 UCT Prague.
# 
# propertyvalue_acls.py is part of Invenio Explicit ACLs 
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
"""Simple ACL matching all records that have a metadata property equal to a given value."""
import enum
import logging

from invenio_accounts.models import User
from invenio_db import db
from sqlalchemy_utils import ChoiceType, Timestamp

from invenio_explicit_acls.models import ACL, gen_uuid_key

from .es_mixin import ESACLMixin

logger = logging.getLogger(__name__)


class MatchOperation(enum.Enum):
    """The operation for matching property to value might be either term or match - choose according to the schema."""

    match = 'match'
    term = 'term'


class BoolOperation(enum.Enum):
    """The ES Bool filter query type."""

    must = 'must'
    """All properties of this type must match. The equivalent of AND."""
    mustNot = 'must_not'
    """All properties of this type must not match. The equivalent of NOT."""
    should = 'should'
    """At least one property must match. The equivalent of OR."""
    filter = 'filter'
    """Properties that must match, but are run in non-scoring, filtering mode."""


class PropertyValue(db.Model, Timestamp):
    """Property and Value match to be used in Property based ACL queries."""

    __tablename__ = 'explicit_acls_propertyvalue'

    #
    # Fields
    #
    id = db.Column(
        db.String(36),
        default=gen_uuid_key,
        primary_key=True
    )
    """Primary key."""

    acl_id = db.Column(db.ForeignKey('explicit_acls_propertyvalueacl.id',
                                     name='fk_explicit_acls_propertyvalue_acl_id'))
    acl = db.relationship('PropertyValueACL', back_populates='property_values')

    name = db.Column(db.String(64))
    """Name of the property in elasticsearch."""

    value = db.Column(db.String(128))
    """Value of the property in elasticsearch."""

    match_operation = db.Column(ChoiceType(MatchOperation, impl=db.String(length=10)),
                                default=MatchOperation.term)
    """Property value matching mode: can be either term or match."""

    bool_operation = db.Column(ChoiceType(BoolOperation, impl=db.String(length=10)), default=BoolOperation.must)
    """Bool filter operation mode this property belongs to."""

    originator_id = db.Column(db.ForeignKey(User.id, ondelete='CASCADE', ),
                              nullable=False, index=True)
    originator = db.relationship(
        User,
        backref=db.backref("authored_properties"))
    """The originator (person that last time modified the Property)"""

    def __str__(self):
        """Returns string representation of the class."""
        return '%s: %s(%s=%s)' % (self.bool_operation, self.match_operation, self.name, self.value, )


class PropertyValueACL(ESACLMixin, ACL):
    """An ACL that matches all records that have a metadata property equal to a given constant value."""

    __tablename__ = 'explicit_acls_propertyvalueacl'
    __mapper_args__ = {
        'polymorphic_identity': 'propertyvalue',
    }

    #
    # Fields
    #
    id = db.Column(db.String(36), db.ForeignKey('explicit_acls_acl.id'), primary_key=True)
    """Id maps to base class' id"""

    property_values = db.relationship("PropertyValue", back_populates="acl")
    """A set of actors for this ACL (who have rights to perform an operation this ACL references)"""

    @property
    def record_selector(self):
        """Returns an elasticsearch query matching resources that this ACL maps to."""
        boolProps = {}

        for prop in self.property_values:  # type: PropertyValue
            boolProps.setdefault(prop.bool_operation.value, []).append(
                {
                    prop.match_operation.value: {
                        prop.name: prop.value
                    }
                }
            )

        return {
            'bool': boolProps
        }

    def __repr__(self):
        """String representation for model."""
        return '"{0.name}" ({0.id}) on schemas {0.schemas}'.format(self)

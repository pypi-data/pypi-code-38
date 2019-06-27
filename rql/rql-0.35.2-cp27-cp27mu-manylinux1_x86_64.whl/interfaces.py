# copyright 2004-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of rql.
#
# rql is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# rql is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with rql. If not, see <http://www.gnu.org/licenses/>.
"""Interfaces used by the RQL package.

"""
__docformat__ = "restructuredtext en"

from logilab.common.interface import Interface


class ISchema(Interface):
    """RQL expects some base types to exists: String, Float, Int, Boolean, Date
    and a base relation : is
    """

    def has_entity(self, etype):
        """Return true if the given type is defined in the schema.
        """

    def has_relation(self, rtype):
        """Return true if the given relation's type is defined in the schema.
        """

    def entities(self, schema=None):
        """Return the list of possible types.

        If schema is not None, return a list of schemas instead of types.
        """

    def relations(self, schema=None):
        """Return the list of possible relations.

        If schema is not None, return a list of schemas instead of relation's
        types.
        """

    def relation_schema(self, rtype):
        """Return the relation schema for the given relation type.
        """


class IRelationSchema(Interface):
    """Interface for Relation schema (a relation is a named oriented link
    between two entities).
    """

    def associations(self):
        """Return a list of (fromtype, [totypes]) defining between which types
        this relation may exists.
        """

    def subjects(self):
        """Return a list of types which can be subject of this relation.
        """

    def objects(self):
        """Return a list of types which can be object of this relation.
        """


class IEntitySchema(Interface):
    """Interface for Entity schema."""

    def is_final(self):
        """Return true if the entity is a final entity (ie cannot be used
        as subject of a relation).
        """

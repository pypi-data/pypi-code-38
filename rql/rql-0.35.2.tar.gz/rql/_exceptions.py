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
"""Exceptions used in the RQL package."""

__docformat__ = "restructuredtext en"


class RQLException(Exception):
    """Base exception for exceptions of the rql module."""


class MissingType(RQLException):
    """Raised when there is some expected type missing from a schema."""


class UsesReservedWord(RQLException):
    """Raised when the schema uses a reserved word as type or relation."""


class RQLSyntaxError(RQLException):
    """Raised when there is a syntax error in the rql string."""


class TypeResolverException(RQLException):
    """Raised when we are unable to guess variables' type."""


class BadRQLQuery(RQLException):
    """Raised when there is a no sense in the rql query."""


class CoercionError(RQLException):
    """Failed to infer type of a math expression."""

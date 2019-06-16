# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Core Data Stuff
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail.core import get_uuid


def uuid_column(*args, **kwargs):
    """
    Returns a UUID column for use as a table's primary key.
    """

    kwargs.setdefault('primary_key', True)
    kwargs.setdefault('nullable', False)
    kwargs.setdefault('default', get_uuid)
    return sa.Column(sa.String(length=32), *args, **kwargs)


def filename_column(*args, **kwargs):
    """
    Returns a SQLAlchemy Column object suitable for representing a filename.
    """
    kwargs.setdefault('nullable', True)
    kwargs.setdefault('doc', "Base name of the data file.")
    return sa.Column(sa.String(length=255), *args, **kwargs)


def getset_factory(collection_class, proxy):
    """
    Get/set factory for SQLAlchemy association proxy attributes.
    """
    def getter(obj):
        if obj is None:
            return None
        return getattr(obj, proxy.value_attr)

    def setter(obj, val):
        setattr(obj, proxy.value_attr, val)

    return getter, setter

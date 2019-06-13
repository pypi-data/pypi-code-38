# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Vendors API
"""

from __future__ import unicode_literals

from sqlalchemy.orm.exc import NoResultFound

from rattail.db import model
from rattail.db.api import get_setting


def get_vendor(session, key):
    """
    Locate and return a vendor for the given key, if possible.

    First the key is assumed to be a ``Vendor.id`` value.  If no matches are
    found, then it looks for a special setting in the database.  If one is
    found, ``get_vendor()`` is called again with its value.

    :param session: Active database session.

    :param key: Value to use when searching for the vendor.  

    :returns: The :class:`rattail.db.model.Vendor` instance if found; otherwise
      ``None``.
    """
    # Vendor.uuid match?
    vendor = session.query(model.Vendor).get(key)
    if vendor:
        return vendor

    # Vendor.id match?
    try:
        return session.query(model.Vendor).filter_by(id=key).one()
    except NoResultFound:
        pass

    # Try settings, if value then recurse.
    key = get_setting(session, 'rattail.vendor.{0}'.format(key))
    if key is None:
        return None
    return get_vendor(session, key)

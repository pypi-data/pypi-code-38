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
API for Store Models
"""

from __future__ import unicode_literals

from sqlalchemy.orm.exc import NoResultFound

from rattail.db import model
from rattail.db.api import get_setting


def get_store(session, key):
    """
    Locate and return a store for the given key, if possible.

    First the key is assumed to be a ``Store.id`` value.  If no matches are
    found, then it looks for a special setting in the database.  If one is
    found, ``get_store()`` is called again with its value.

    :param session: Active database session.

    :param key: Value to use when searching for the store.

    :returns: The :class:`rattail.db.model.Store` instance if found; otherwise
      ``None``.
    """
    # Store.uuid match?
    store = session.query(model.Store).get(key)
    if store:
        return store

    # Store.id match?
    try:
        return session.query(model.Store).filter_by(id=key).one()
    except NoResultFound:
        pass

    # Try settings, if value then recurse.
    key = get_setting(session, 'rattail.store.{0}'.format(key))
    if key:
        return get_store(session, key)

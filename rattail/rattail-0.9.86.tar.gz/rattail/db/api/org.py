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
API for Organizational Models
"""

from __future__ import unicode_literals, absolute_import

import six
from sqlalchemy.orm.exc import NoResultFound

from rattail.db import model
from rattail.db.api import get_setting


def get_department(session, key):
    """
    Locate and return a department for the given key, if possible.

    First the key is assumed to be a ``Department.number`` value.  If no
    matches are found, then it looks for a special setting in the database.  If
    one is found, ``get_department()`` is called again with its value.

    :param session: Active database session.

    :param key: Value to use when searching for the department.  

    :returns: The :class:`rattail.db.model.Department` instance if found;
      otherwise ``None``.
    """
    # Department.uuid match?
    department = session.query(model.Department).get(six.text_type(key))
    if department:
        return department

    # Department.number match?
    if isinstance(key, int) or key.isdigit():
        try:
            return session.query(model.Department).filter_by(number=key).one()
        except NoResultFound:
            pass

    # Try settings, if value then recurse.
    key = get_setting(session, 'rattail.department.{0}'.format(key))
    if key is None:
        return None
    return get_department(session, key)


def get_subdepartment(session, key):
    """
    Locate and return a subdepartment for the given key, if possible.

    First the key is assumed to be a ``Subdepartment.number`` value.  If no
    matches are found, then it looks for a special setting in the database.  If
    one is found, ``get_subdepartment()`` is called again with its value.

    :param session: Active database session.

    :param key: Value to use when searching for the subdepartment.  

    :returns: The :class:`rattail.db.model.Subdepartment` instance if found;
      otherwise ``None``.
    """
    # Subdepartment.uuid match?
    subdepartment = session.query(model.Subdepartment).get(key)
    if subdepartment:
        return subdepartment

    # Subdepartment.number match?
    if isinstance(key, int) or key.isdigit():
        try:
            return session.query(model.Subdepartment).filter_by(number=key).one()
        except NoResultFound:
            pass

    # Try settings, if value then recurse.
    key = get_setting(session, 'rattail.subdepartment.{0}'.format(key))
    if key is None:
        return None
    return get_subdepartment(session, key)

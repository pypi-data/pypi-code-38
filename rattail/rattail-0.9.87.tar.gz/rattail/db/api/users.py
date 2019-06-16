# -*- coding: utf-8; -*-
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
Users API
"""

from __future__ import unicode_literals, absolute_import

import six
from sqlalchemy import orm

from rattail.db import model


def make_username(person):
    """
    Make up a new username for the given person.  Takes the often-used approach
    of first initial plus last name, e.g. 'ledgar' for Lance Edgar.  Appends an
    autoincrement number if necessary, until a unique name is found.
    """
    session = orm.object_session(person)
    users = session.query(model.User)

    basename = (person.last_name or '').strip().lower()
    if basename:
        if (person.first_name or '').strip():
            basename = '{}{}'.format((person.first_name or '').strip().lower()[0],
                                     basename)
    else:
        basename = (person.first_name or '').strip().lower()

    if basename:
        i = 0
        username = basename
    else:
        i = 1
        username = six.text_type(i)
    while users.filter_by(username=username).count():
        i += 1
        username = '{}{}'.format(basename, i)

    return username

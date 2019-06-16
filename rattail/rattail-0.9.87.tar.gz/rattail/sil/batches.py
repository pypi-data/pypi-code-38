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
Batch Stuff
"""

from __future__ import unicode_literals, absolute_import

from six.moves import configparser

import six
import lockfile

from rattail.config import get_user_file


def consume_batch_id(source='RATAIL'):
    """
    Returns the next available batch identifier for ``source``, incrementing
    the number to preserve uniqueness.
    """
    path = get_user_file('rattail.conf', createdir=True)
    with lockfile.LockFile(path):

        parser = configparser.SafeConfigParser()
        parser.read(path)
        option = 'next_batch_id.{0}'.format(source)

        batch_id = 1
        if parser.has_section('rattail.sil'):
            if parser.has_option('rattail.sil', option):
                batch_id = parser.get('rattail.sil', option)
                batch_id = int(batch_id) if batch_id.isdigit() else 1

        if not parser.has_section('rattail.sil'):
            parser.add_section('rattail.sil')
        parser.set('rattail.sil', option, six.text_type(batch_id + 1))

        with open(path, 'wt') as f:
            parser.write(f)

    return '{0:08d}'.format(batch_id)

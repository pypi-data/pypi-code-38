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
PostgreSQL data importers
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import logging

import six

from rattail.importing import BulkImporter, ToSQLAlchemy
from rattail.time import make_utc


log = logging.getLogger(__name__)


class BulkToPostgreSQL(BulkImporter, ToSQLAlchemy):
    """
    Base class for bulk data importers which target PostgreSQL on the local side.
    """

    @property
    def data_path(self):
        return os.path.join(self.config.workdir(),
                            'import_bulk_postgresql_{}.csv'.format(self.model_name))

    def setup(self):
        self.data_buffer = open(self.data_path, 'wb')

    def teardown(self):
        self.data_buffer.close()
        os.remove(self.data_path)
        self.data_buffer = None

    def create_object(self, key, data):
        data = self.prep_data_for_postgres(data)
        self.data_buffer.write('{}\n'.format('\t'.join([data[field] for field in self.fields])).encode('utf-8'))

    def prep_data_for_postgres(self, data):
        data = dict(data)
        for key, value in data.items():
            data[key] = self.prep_value_for_postgres(value)
        return data

    def prep_value_for_postgres(self, value):
        if value is None:
            return '\\N'
        if value is True:
            return 't'
        if value is False:
            return 'f'

        if isinstance(value, datetime.datetime):
            value = make_utc(value, tzinfo=False)
        elif isinstance(value, six.string_types):
            value = value.replace('\\', '\\\\')
            value = value.replace('\r', '\\r')
            value = value.replace('\n', '\\n')
            value = value.replace('\t', '\\t') # TODO: add test for this

        return six.text_type(value)

    def flush_create_update(self):
        pass

    def flush_create_update_final(self):
        log.info("copying {} data from buffer to PostgreSQL".format(self.model_name))
        self.data_buffer.close()
        self.data_buffer = open(self.data_path, 'rb')
        cursor = self.session.connection().connection.cursor()
        table_name = '"{}"'.format(self.model_table.name)
        cursor.copy_from(self.data_buffer, table_name, columns=self.fields)
        log.debug("PostgreSQL data copy completed")

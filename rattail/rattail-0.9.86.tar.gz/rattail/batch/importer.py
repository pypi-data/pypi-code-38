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
Handler for importer batches
"""

from __future__ import unicode_literals, absolute_import

import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model
from rattail.batch import BatchHandler
from rattail.util import load_object


log = logging.getLogger(__name__)


class ImporterBatchHandler(BatchHandler):
    """
    Handler for importer batches.
    """
    batch_model_class = model.ImporterBatch

    def execute(self, batch, user=None, progress=None, **kwargs):
        session = orm.object_session(batch)
        metadata = sa.MetaData(schema='batch', bind=session.bind)
        row_table = sa.Table(batch.row_table, metadata, autoload=True)

        handler = load_object(batch.import_handler_spec)(config=self.config)
        handler.runas_user = user
        handler.setup()
        handler.begin_transaction()

        importer = handler.get_importer(batch.importer_key)
        assert importer
        importer.setup()

        def process(row, i):

            if row.status_code == self.enum.IMPORTER_BATCH_ROW_STATUS_CREATE:
                host_data = {}
                for col in row_table.c:
                    if col.name.startswith('key_'):
                        field = col.name[4:]
                        host_data[field] = getattr(row, col.name)
                    elif col.name.startswith('post_'):
                        field = col.name[5:]
                        host_data[field] = getattr(row, col.name)
                key = importer.get_key(host_data)
                local_object = importer.create_object(key, host_data)
                log.debug("created new %s %s: %s", importer.model_name, key, local_object)

            elif row.status_code == self.enum.IMPORTER_BATCH_ROW_STATUS_UPDATE:
                host_data = {}
                local_data = {}
                for col in row_table.c:
                    if col.name.startswith('key_'):
                        field = col.name[4:]
                        host_data[field] = getattr(row, col.name)
                        local_data[field] = getattr(row, col.name)
                    elif col.name.startswith('pre_'):
                        field = col.name[4:]
                        local_data[field] = getattr(row, col.name)
                    elif col.name.startswith('post_'):
                        field = col.name[5:]
                        host_data[field] = getattr(row, col.name)
                key = importer.get_key(host_data)
                local_object = importer.get_local_object(key)
                local_object = importer.update_object(local_object, host_data, local_data)
                log.debug("updated %s %s: %s", importer.model_name, key, local_object)

            elif row.status_code == self.enum.IMPORTER_BATCH_ROW_STATUS_DELETE:
                host_data = {}
                for col in row_table.c:
                    if col.name.startswith('key_'):
                        field = col.name[4:]
                        host_data[field] = getattr(row, col.name)
                key = importer.get_key(host_data)
                local_object = importer.get_local_object(key)
                text = six.text_type(local_object)
                importer.delete_object(local_object)
                log.debug("deleted %s %s: %s", importer.model_name, key, text)

        rows = session.query(row_table)
        self.progress_loop(process, rows, progress,
                           message="Executing import / export batch")

        importer.teardown()
        handler.teardown()
        handler.commit_transaction()
        return True

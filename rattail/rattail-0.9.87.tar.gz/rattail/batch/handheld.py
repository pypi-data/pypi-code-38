# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Handheld batch handler
"""

from __future__ import unicode_literals, absolute_import

import csv
import decimal

import six
from sqlalchemy import orm

from rattail.db import api, model
from rattail.batch import BatchHandler, get_batch_handler
from rattail.gpc import GPC
from rattail.time import make_utc
from rattail.wince import parse_batch_file as parse_wince_file


class HandheldBatchHandler(BatchHandler):
    """
    Handler for handheld batches.
    """
    batch_model_class = model.HandheldBatch

    def should_populate(self, batch):
        # all handheld batches must come from input data file
        return True

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from an input data file, parsed according
        to the batch device type.
        """
        if not batch.filename:
            raise ValueError("Batch must have a filename: {}".format(batch))
        if not batch.device_type:
            raise ValueError("Batch must have a device_type: {}".format(batch))
        batch.rowcount = 0

        def append(entry, i):
            upc, cases, units = entry
            row = model.HandheldBatchRow(upc=upc, cases=cases, units=units)
            batch.add_row(row)
            self.refresh_row(row)
            batch.rowcount += 1

        parse = getattr(self, 'parse_input_file_{}'.format(batch.device_type))
        entries = parse(batch.absolute_filepath(self.config), progress=progress)
        self.progress_loop(append, entries, progress,
                           message="Adding initial rows to batch")

    def refresh_batch_status(self, batch):
        if any([row.status_code != row.STATUS_OK for row in batch.active_rows()]):
            batch.status_code = batch.STATUS_QUESTIONABLE
        else:
            batch.status_code = batch.STATUS_OK

    def parse_input_file_motorola(self, path, progress=None):
        """
        Parse a RattailCE (binary or CSV) file to generate initial rows.
        """
        data = []
        filemode = 'rt' if six.PY3 else 'rb'
        with open(path, filemode) as f:
            line = f.readline()

        if '\x00' in line:      # raw binary file from RattailCE app

            def convert(entry, i):
                scancode, cases, units = entry
                upc = GPC(int(scancode), calc_check_digit='upc')
                data.append((
                    upc,
                    cases or None,
                    units or None,
                ))

            entries = list(parse_wince_file(path, progress=progress))

        else:                   # presumably csv, converted from raw file

            def convert(entry, i):
                upc = GPC(entry['upc'], calc_check_digit='upc')
                data.append((
                    upc,
                    decimal.Decimal(entry['cases']) if entry['cases'] else None,
                    decimal.Decimal(entry['units']) if entry['units'] else None,
                ))

            with open(path, filemode) as f:
                reader = csv.DictReader(f)
                entries = list(reader)

        self.progress_loop(convert, entries, progress,
                           message="Normalizing data from WinCE file")
        return data

    def parse_input_file_palmos(self, path, progress=None):
        """
        Parse a Rattail PalmOS (CSV) file to generate initial rows.
        """
        data = []

        def convert(entry, i):
            data.append((
                GPC(entry['upc'], calc_check_digit='upc'),
                int(entry['cases']),
                int(entry['units']),
            ))

        with open(path, 'rb') as f:
            reader = csv.DictReader(f)
            entries = list(reader)

        if self.progress_loop(convert, entries, progress,
                              message="Normalizing data from PalmOS file"):
            return data

    def refresh_row(self, row):
        """
        This method will be passed a row object which has already been properly
        added to a batch, and which has basic required fields already
        populated.  This method is then responsible for further populating all
        applicable fields for the row, based on current data within the
        relevant system(s).

        Note that in some cases this method may be called multiple times for
        the same row, e.g. once when first creating the batch and then later
        when a user explicitly refreshes the batch.  The method logic must
        account for this possibility.
        """
        if not row.upc:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        session = orm.object_session(row)
        product = api.get_product_by_upc(session, row.upc)
        if not product:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        # current / static attributes
        row.product = product
        row.brand_name = product.brand.name if product.brand else None
        row.description = product.description
        row.size = product.size
        row.status_code = row.STATUS_OK

    def execute(self, batch, user=None, action='make_inventory_batch', progress=None, **kwargs):
        return self.execute_many([batch], user=user, action=action, progress=progress, **kwargs)

    def execute_many(self, batches, user=None, action='make_inventory_batch', progress=None, **kwargs):
        batches = [batch for batch in batches if not batch.executed]
        if not batches:
            return True
        if action == 'make_inventory_batch':
            result = self.make_inventory_batch(batches, user, progress=progress)
        elif action == 'make_label_batch':
            result = self.make_label_batch(batches, user, progress=progress)
        else:
            raise RuntimeError("Batch execution action is not supported: {}".format(action))
        now = make_utc()
        for batch in batches:
            batch.executed = now
            batch.executed_by = user
        return result

    def make_inventory_batch(self, handheld_batches, user, progress=None):
        handler = get_batch_handler(self.config, 'inventory',
                                    default='rattail.batch.inventory:InventoryBatchHandler')
        session = orm.object_session(handheld_batches[0])
        batch = handler.make_batch(session, created_by=user, handheld_batches=handheld_batches)
        handler.do_populate(batch, user, progress=progress)
        return batch

    def make_label_batch(self, handheld_batches, user, progress=None):
        handler = get_batch_handler(self.config, 'labels',
                                    default='rattail.batch.labels:LabelBatchHandler')
        session = orm.object_session(handheld_batches[0])
        batch = handler.make_batch(session, created_by=user, handheld_batches=handheld_batches)
        handler.do_populate(batch, user, progress=progress)
        return batch

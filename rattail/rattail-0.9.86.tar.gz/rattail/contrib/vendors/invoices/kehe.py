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
Vendor invoice parser for KeHE Distributors
"""

from __future__ import unicode_literals, absolute_import

import re
import csv
import datetime

import six

from rattail.db import model
from rattail.gpc import GPC
from rattail.vendors.invoices import InvoiceParser


class KeheInvoiceParser(InvoiceParser):
    """
    Vendor invoice parser for KeHE Distributors.
    """
    key = 'rattail.contrib.kehe'
    display = "KeHE Distributors"
    vendor_key = 'kehe'

    pack_size_pattern = re.compile('^(?P<case_quantity>\d+)/(?P<size>\d*\.\d+ \w\w)$')

    def parse_invoice_date(self, path):
        if six.PY3:
            csv_file = open(path, 'rt')
            reader = csv.DictReader(csv_file, delimiter='\t')
        else: # PY2
            csv_file = open(path, 'rb')
            reader = csv.DictReader(csv_file, delimiter=b'\t')
        data = next(reader)
        csv_file.close()
        return datetime.datetime.strptime(data['Invoice Date'], '%Y-%m-%d').date()

    def parse_rows(self, path):
        if six.PY3:
            csv_file = open(path, 'rt')
            reader = csv.DictReader(csv_file, delimiter='\t')
        else: # PY2
            csv_file = open(path, 'rb')
            reader = csv.DictReader(csv_file, delimiter=b'\t')

        for data in reader:

            row = model.VendorInvoiceRow()
            row.item_entry = data['UPC Code']
            row.upc = GPC(row.item_entry)
            row.vendor_code = data['Ship Item']
            row.brand_name = data['Brand']
            row.description = data['Description']
            row.ordered_units = self.int_(data['Order Qty'])
            row.shipped_units = self.int_(data['Ship Qty'])
            row.unit_cost = self.decimal(data['Net Each'])
            row.total_cost = self.decimal(data['Net Billable'])

            # Case quantity may be embedded in size string.
            row.size = data['Pack Size']
            row.case_quantity = 1
            match = self.pack_size_pattern.match(row.size)
            if match:
                row.case_quantity = int(match.group('case_quantity'))
                row.size = match.group('size')

            # attach original raw data to the row we're returning; caller
            # can use as needed, or ignore
            row._raw_data = data

            yield row

        csv_file.close()

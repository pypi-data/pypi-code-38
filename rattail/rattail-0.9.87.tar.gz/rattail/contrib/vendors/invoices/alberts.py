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
Vendor invoice parser for Albert's Organics
"""

from __future__ import unicode_literals, absolute_import

import csv
import datetime

import six

from rattail.db import model
from rattail.gpc import GPC
from rattail.vendors.invoices import InvoiceParser


class AlbertsInvoiceParser(InvoiceParser):
    """
    Invoice parser for Albert's Organics CSV files.
    """
    key = 'rattail.contrib.alberts'
    display = "Albert's Organics"
    vendor_key = 'alberts'

    def parse_invoice_date(self, path):
        if six.PY3:
            csv_file = open(path, 'rt')
        else: # PY2
            csv_file = open(path, 'rb')
        reader = csv.DictReader(csv_file)
        data = next(reader)
        csv_file.close()
        return datetime.datetime.strptime(data['Invoice Date'], '%m/%d/%Y').date()

    def parse_rows(self, path):
        if six.PY3:
            csv_file = open(path, 'rt')
        else: # PY2
            csv_file = open(path, 'rb')

        reader = csv.DictReader(csv_file)
        for data in reader:

            row = model.VendorInvoiceRow()
            row.item_entry = data['UPCPLU'].replace('-', '').replace(' ', '')
            row.upc = GPC(row.item_entry)
            row.vendor_code = data['ItemNumber']
            row.brand_name = data['BrandName']
            row.description = data['MV']
            row.size = "{} {}".format(data['PkgSize'], data['UOMAbbr'])
            row.case_quantity = self.int_(data['PkgCount'])
            if not row.case_quantity:
                row.case_quantity = self.decimal(data['PkgSize'])
                if row.case_quantity:
                    row.case_quantity = int(row.case_quantity)
            row.shipped_cases = self.decimal(data['ShipQty'])
            row.case_cost = self.decimal(data['CasePrice'])
            row.unit_cost = self.decimal(data['EachPrice'])
            row.total_cost = row.case_cost * row.shipped_cases

            yield row

        csv_file.close()

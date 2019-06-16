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
Vendor catalog parser for United Natural Foods (UNFI)
"""

from __future__ import unicode_literals, absolute_import

import re
import datetime
from decimal import Decimal

import six
import xlrd

from rattail.db import model
from rattail.gpc import GPC
from rattail.vendors.catalogs import CatalogParser


class UNFICatalogParser(CatalogParser):
    """
    Vendor catalog parser for UNFI, version 1.
    """
    key = 'rattail.contrib.unfi'
    display = "United Natural Foods (UNFI), v1"
    vendor_key = 'unfi'

    effective_date_pattern = re.compile(r'effective from (\d{2}/\d{2}/\d{4})-')
    code_pattern = re.compile(r'^\d{6}-\d$')
    upc_pattern = re.compile(r'^\d-\d{5}-\d{5}-\d$')

    def open_sheet(self, path):
        book = xlrd.open_workbook(path)
        return book.sheet_by_index(0)

    def parse_effective_date(self, path):
        sheet = self.open_sheet(path)
        text = sheet.cell_value(0, 0)
        match = self.effective_date_pattern.search(text)
        if match:
            return datetime.datetime.strptime(match.group(1), '%m/%d/%Y').date()

    def parse_rows(self, path, progress=None):
        sheet = self.open_sheet(path)
        for r in range(sheet.nrows):

            # Use the code to determine if the row is valid.
            code = sheet.cell_value(r, 0)
            if not self.code_pattern.match(code):
                continue

            # Warn if UPC is not valid.
            upc = sheet.cell_value(r, 1)
            if self.upc_pattern.match(upc):
                upc = GPC(upc.replace('-', ''))
            else:
                log.warning("invalid upc at row {0}: {1}".format(r + 1, upc))
                upc = None

            row = model.VendorCatalogRow()
            row.upc = upc
            row.vendor_code = code.replace('-', '')
            row.brand_name = sheet.cell_value(r, 2)
            row.description = sheet.cell_value(r, 3)
            row.size = sheet.cell_value(r, 5)
            row.case_size = int(sheet.cell_value(r, 4))
            row.case_cost = Decimal(six.text_type(sheet.cell_value(r, 8)))
            row.unit_cost = Decimal(six.text_type(sheet.cell_value(r, 9)))
            yield row


class UNFICatalogParser2(UNFICatalogParser):
    """
    Vendor catalog parser for UNFI, version 2.
    """
    key = 'rattail.contrib.unfi.2'
    display = "United Natural Foods (UNFI), v2"

    def parse_rows(self, path, progress=None):
        sheet = self.open_sheet(path)
        for r in range(sheet.nrows):

            # Use the code to determine if the row is valid.
            code = sheet.cell_value(r, 0)
            if not self.code_pattern.match(code):
                continue

            # Warn if UPC is not valid.
            upc = sheet.cell_value(r, 1)
            if self.upc_pattern.match(upc):
                upc = GPC(upc.replace('-', ''))
            else:
                log.warning("invalid upc at row {0}: {1}".format(r + 1, upc))
                upc = None

            row = model.VendorCatalogRow()
            row.upc = upc
            row.vendor_code = code.replace('-', '')
            row.brand_name = sheet.cell_value(r, 2)
            row.description = sheet.cell_value(r, 4)
            row.size = sheet.cell_value(r, 7)
            row.case_size = int(sheet.cell_value(r, 6))
            row.case_cost = Decimal(six.text_type(sheet.cell_value(r, 10)))
            row.unit_cost = Decimal(six.text_type(sheet.cell_value(r, 11)))
            yield row

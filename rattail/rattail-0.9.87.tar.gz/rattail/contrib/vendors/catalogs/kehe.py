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
Vendor catalog parser for KeHE Distributors
"""

from __future__ import unicode_literals, absolute_import

import os
import re
import datetime
import decimal
import logging

import xlrd
from sqlalchemy.orm import joinedload

from rattail.db import model
from rattail.db.cache import cache_model
from rattail.gpc import GPC
from rattail.vendors.catalogs import CatalogParser


log = logging.getLogger(__name__)


class KeheCatalogParser(CatalogParser):
    """
    Vendor catalog parser for KeHE Distributors.
    """
    key = 'rattail.contrib.kehe'
    display = "KeHE Distributors"
    vendor_key = 'kehe'

    def parse_effective_date(self, path):
        """
        This parser does not expect to find an effective date within the
        catalog file itself, but it makes a feeble attempt at gleaning it from
        the filename.  The example used to create this code was:

        .. code-block:: none

           DC22 CNP Catalog - February 2015.xls
        """
        basename = os.path.basename(path)
        match = re.search(r' (\w{3} \d{4})\.xls$', basename)
        if match:
            return datetime.datetime.strptime(match.group(1), '%b %Y').date()

    def parse_rows(self, path, progress=None):
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_index(0)
        products = cache_model(self.session, model.Product, key='upc',
                               query_options=[joinedload(model.Product.costs),
                                              joinedload(model.Product.cost)])

        for r in range(1, sheet.nrows): # Skip first header row.

            row = model.VendorCatalogRow()
            upc = sheet.cell_value(r, 5) or None
            row.upc = GPC(int(upc)) if upc else None
            row.brand_name = sheet.cell_value(r, 1)
            row.description = sheet.cell_value(r, 2)
            row.size = sheet.cell_value(r, 3)
            row.vendor_code = '{0:07d}'.format(int(sheet.cell_value(r, 0)))

            # KeHE catalogs sort of have two columns to represent case size.
            # Sometimes the "Case Pack" column is what we want; other times
            # it's the "Un of Sls" column.  There appears to be no way to
            # really know which should be used, so we must query the database
            # to determine which case size is already in effect for the
            # product.  If that doesn't work, then we're back to guessing; we
            # use the "Case Pack" column in that case.
            case_pack = int(sheet.cell_value(r, 6))
            unit_of_sales = int(sheet.cell_value(r, 7))
            if row.upc:
                product = products.get(row.upc)
                if product:

                    # First we try to find an existing cost record for KeHE.  If
                    # one exists, we will honor its case size.
                    cost = product.cost_for_vendor(self.vendor)
                    if cost:
                        if cost.case_size == case_pack:
                            row.case_size = case_pack
                        elif cost.case_size == unit_of_sales:
                            row.case_size = unit_of_sales

                    # If there was no KeHE cost record, then we'll honor the
                    # "preferred" cost record case size, if it has one.
                    if row.case_size is None and product.cost:
                        if product.cost.case_size == case_pack:
                            row.case_size = case_pack
                        elif product.cost.case_size == unit_of_sales:
                            row.case_size = unit_of_sales

            # If all else fails, use the "Case Pack" column.
            if row.case_size is None:
                row.case_size = case_pack

            try:
                row.unit_cost = decimal.Decimal('{:0.4f}'.format(sheet.cell_value(r, 8)))
            except ValueError:
                log.warning("invalid unit cost for UPC {} at row {}: {}".format(row.upc, r + 1, sheet.cell_value(r, 8)))
            else:
                row.case_cost = row.unit_cost * row.case_size
            yield row

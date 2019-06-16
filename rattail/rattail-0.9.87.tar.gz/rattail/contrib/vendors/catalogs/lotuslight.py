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
Vendor catalog parser for Lotus Light
"""

from __future__ import unicode_literals, absolute_import

import os
import re
import datetime
import logging

import xlrd

from rattail.db import model
from rattail.gpc import GPC
from rattail.vendors.catalogs import CatalogParser


log = logging.getLogger(__name__)


class LotusLightCatalogParser(CatalogParser):
    """
    Vendor catalog parser for Lotus Light.
    """
    key = 'rattail.contrib.lotuslight'
    display = "Lotus Light"
    vendor_key = 'lotus-light'

    def parse_effective_date(self, path):
        """
        This parser does not expect to find an effective date within the
        catalog file itself, but it makes a feeble attempt at gleaning it from
        the filename.  The example used to create this code was:

        .. code-block:: none

           Lotus Light Catalog Nov 2012.xls
        """
        basename = os.path.basename(path)
        match = re.match(r'^Lotus Light Catalog (\w{3} \d{4})\.xls$', basename)
        if match:
            return datetime.datetime.strptime(match.group(1), '%b %Y').date()

    def parse_rows(self, path, progress=None):
        """
        Parse data rows from a catalog file.
        """
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_index(0)
        for i in range(1, sheet.nrows): # skip first header row

            row = model.VendorCatalogRow()

            upc = sheet.cell_value(i, 1)
            if upc:
                if upc.isdigit():
                    # Sometimes their catalog doesn't include the check digit..?
                    if len(upc) == 11:
                        row.upc = GPC(int(upc), calc_check_digit='upc')
                    else:
                        row.upc = GPC(int(upc))
                else:
                    log.warning("invalid UPC at row {0}: {1}".format(i + 1, repr(upc)))

            row.brand_name = sheet.cell_value(i, 2)
            row.description = sheet.cell_value(i, 4)
            row.vendor_code = sheet.cell_value(i, 0)
            row.case_quantity = 1
            row.unit_cost = self.decimal(sheet.cell_value(i, 7))
            row.case_cost = row.unit_cost
            yield row

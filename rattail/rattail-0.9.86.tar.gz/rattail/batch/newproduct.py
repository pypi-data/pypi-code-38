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
Handler for new product batches
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model
from rattail.gpc import GPC
from rattail.batch import BatchHandler


class NewProductBatchHandler(BatchHandler):
    """
    Handler for new product batches.
    """
    batch_model_class = model.NewProductBatch

    def should_populate(self, batch):
        if batch.input_filename:
            return True
        return False

    def populate(self, batch, progress=None):
        if batch.input_filename:
            return self.populate_from_file(batch, progress=progress)

    def populate_from_file(self, batch, progress=None):
        raise NotImplementedError

    def refresh_row(self, row):
        session = orm.object_session(row)

        row.upc = GPC(row.item_entry, calc_check_digit='auto')

        # vendor
        if row.vendor_id:
            row.vendor = session.query(model.Vendor)\
                                .filter(model.Vendor.id == row.vendor_id)\
                                .first()
        else:
            row.vendor = None

        # department
        if row.department_number:
            row.department = session.query(model.Department)\
                                    .filter(model.Department.number == row.department_number)\
                                    .first()
        else:
            row.department = None

        # subdepartment
        if row.subdepartment_number:
            row.subdepartment = session.query(model.Subdepartment)\
                                       .filter(model.Subdepartment.number == row.subdepartment_number)\
                                       .first()
        else:
            row.subdepartment = None

        # category
        if row.category_code:
            row.category = session.query(model.Category)\
                                  .filter(model.Category.code == row.category_code)\
                                  .first()
        else:
            row.category = None

        # family
        if row.family_code:
            row.family = session.query(model.Family)\
                                .filter(model.Family.code == row.family_code)\
                                .first()
        else:
            row.family = None

        # report
        if row.report_code:
            row.report = session.query(model.ReportCode)\
                                .filter(model.ReportCode.code == row.report_code)\
                                .first()
        else:
            row.report = None

        # brand
        if row.brand_name:
            row.brand = session.query(model.Brand)\
                               .filter(model.Brand.name == row.brand_name)\
                               .first()
        else:
            row.brand = None

        if not row.product:
            if not row.item_entry:
                row.status_code = row.STATUS_MISSING_KEY
                return

            row.product = self.locate_product_for_entry(session, row.item_entry)

        if row.product:
            row.status_code = row.STATUS_PRODUCT_EXISTS
            return

        if row.vendor_id and not row.vendor:
            row.status_code = row.STATUS_VENDOR_NOT_FOUND
            return

        if row.department_number and not row.department:
            row.status_code = row.STATUS_DEPT_NOT_FOUND
            return

        if row.subdepartment_number and not row.subdepartment:
            row.status_code = row.STATUS_SUBDEPT_NOT_FOUND
            return

        if row.category_code and not row.category:
            row.status_code = row.STATUS_CATEGORY_NOT_FOUND
            return

        if row.family_code and not row.family:
            row.status_code = row.STATUS_FAMILY_NOT_FOUND
            return

        if row.report_code and not row.report:
            row.status_code = row.STATUS_REPORTCODE_NOT_FOUND
            return

        row.status_code = row.STATUS_OK

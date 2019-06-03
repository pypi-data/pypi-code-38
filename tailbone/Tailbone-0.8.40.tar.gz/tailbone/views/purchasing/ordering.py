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
Views for 'ordering' (purchasing) batches
"""

from __future__ import unicode_literals, absolute_import

import os

import six
import openpyxl
from sqlalchemy import orm

from rattail.db import model, api
from rattail.core import Object
from rattail.time import localtime

from webhelpers2.html import tags

from tailbone.views.purchasing import PurchasingBatchView


class OrderingBatchView(PurchasingBatchView):
    """
    Master view for purchase order batches.
    """
    route_prefix = 'ordering'
    url_prefix = '/ordering'
    model_title = "Ordering Batch"
    model_title_plural = "Ordering Batches"
    index_title = "Ordering"
    mobile_creatable = True
    rows_editable = True
    mobile_rows_creatable = True
    mobile_rows_quickable = True
    mobile_rows_editable = True
    mobile_rows_deletable = True
    has_worksheet = True

    mobile_form_fields = [
        'vendor',
        'department',
        'date_ordered',
        'po_number',
        'po_total',
        'created',
        'created_by',
        'notes',
        'status_code',
        'complete',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        # 'item_id',
        'brand_name',
        'description',
        'size',
        'cases_ordered',
        'units_ordered',
        # 'cases_received',
        # 'units_received',
        'po_total',
        # 'invoice_total',
        # 'credits',
        'status_code',
    ]

    order_form_header_columns = [
        "UPC",
        "Brand",
        "Description",
        "Case",
        "Vend. Code",
        "Pref.",
        "Unit Cost",
    ]

    @property
    def batch_mode(self):
        return self.enum.PURCHASE_BATCH_MODE_ORDERING

    def configure_form(self, f):
        super(OrderingBatchView, self).configure_form(f)

        # purchase
        f.remove_field('purchase')

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(OrderingBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        kwargs['ship_method'] = batch.ship_method
        kwargs['notes_to_vendor'] = batch.notes_to_vendor
        return kwargs

    def worksheet(self):
        """
        View for editing batch row data as an order form worksheet.
        """
        batch = self.get_instance()
        if batch.executed:
            return self.redirect(self.get_action_url('view', batch))

        # organize existing batch rows by product
        order_items = {}
        for row in batch.active_rows():
            order_items[row.product_uuid] = row

        # organize vendor catalog costs by dept / subdept
        departments = {}
        costs = self.get_order_form_costs(batch.vendor)
        costs = self.sort_order_form_costs(costs)
        for cost in costs:

            department = cost.product.department
            if department:
                departments.setdefault(department.uuid, department)
            else:
                if None not in departments:
                    department = Object(name='', number=None)
                    departments[None] = department
                department = departments[None]
            
            subdepartments = getattr(department, '_order_subdepartments', None)
            if subdepartments is None:
                subdepartments = department._order_subdepartments = {}

            subdepartment = cost.product.subdepartment
            if subdepartment:
                subdepartments.setdefault(subdepartment.uuid, subdepartment)
            else:
                if None not in subdepartments:
                    subdepartment = Object(name=None, number=None)
                    subdepartments[None] = subdepartment
                subdepartment = subdepartments[None]

            subdept_costs = getattr(subdepartment, '_order_costs', None)
            if subdept_costs is None:
                subdept_costs = subdepartment._order_costs = []
            subdept_costs.append(cost)
            cost._batchrow = order_items.get(cost.product_uuid)

            # do anything else needed to satisfy template display requirements etc.
            self.decorate_order_form_cost(cost)

        # fetch recent purchase history, sort/pad for template convenience
        history = self.get_order_form_history(batch, costs, 6)
        for i in range(6 - len(history)):
            history.append(None)
        history = list(reversed(history))

        title = self.get_instance_title(batch)
        order_date = batch.date_ordered
        if not order_date:
            order_date = localtime(self.rattail_config).date()
        return self.render_to_response('worksheet', {
            'batch': batch,
            'order_date': order_date,
            'instance': batch,
            'instance_title': title,
            'instance_url': self.get_action_url('view', batch),
            'vendor': batch.vendor,
            'departments': departments,
            'history': history,
            'get_upc': lambda p: p.upc.pretty() if p.upc else '',
            'header_columns': self.order_form_header_columns,
            'ignore_cases': not self.handler.allow_cases(),
        })

    def get_order_form_history(self, batch, costs, count):

        # fetch last 6 purchases for this vendor, organize line items by product
        history = []
        purchases = self.Session.query(model.Purchase)\
                                .filter(model.Purchase.vendor == batch.vendor)\
                                .filter(model.Purchase.status >= self.enum.PURCHASE_STATUS_ORDERED)\
                                .order_by(model.Purchase.date_ordered.desc(), model.Purchase.created.desc())\
                                .options(orm.joinedload(model.Purchase.items))
        for purchase in purchases[:count]:
            items = {}
            for item in purchase.items:
                items[item.product_uuid] = item
            history.append({'purchase': purchase, 'items': items})
        
        return history

    def get_order_form_costs(self, vendor):
        return self.Session.query(model.ProductCost)\
                           .join(model.Product)\
                           .outerjoin(model.Brand)\
                           .filter(model.ProductCost.vendor == vendor)\
                           .options(orm.joinedload(model.ProductCost.product)\
                                    .joinedload(model.Product.department))\
                           .options(orm.joinedload(model.ProductCost.product)\
                                    .joinedload(model.Product.subdepartment))

    def sort_order_form_costs(self, costs):
        return costs.order_by(model.Brand.name,
                              model.Product.description,
                              model.Product.size)

    def decorate_order_form_cost(self, cost):
        pass

    def worksheet_update(self):
        """
        Handles AJAX requests to update current batch, from Order Form view.
        """
        batch = self.get_instance()

        cases_ordered = self.request.POST.get('cases_ordered', '0')
        if not cases_ordered or not cases_ordered.isdigit():
            return {'error': "Invalid value for cases ordered: {}".format(cases_ordered)}
        cases_ordered = int(cases_ordered)
        if cases_ordered >= 100000: # TODO: really this depends on underlying column
            return {'error': "Invalid value for cases ordered: {}".format(cases_ordered)}

        units_ordered = self.request.POST.get('units_ordered', '0')
        if not units_ordered or not units_ordered.isdigit():
            return {'error': "Invalid value for units ordered: {}".format(units_ordered)}
        units_ordered = int(units_ordered)
        if units_ordered >= 100000: # TODO: really this depends on underlying column
            return {'error': "Invalid value for units ordered: {}".format(units_ordered)}

        uuid = self.request.POST.get('product_uuid')
        product = self.Session.query(model.Product).get(uuid) if uuid else None
        if not product:
            return {'error': "Product not found"}

        row = None
        rows = [r for r in batch.data_rows if r.product_uuid == uuid]
        if rows:
            assert len(rows) == 1
            row = rows[0]
            if row.po_total and not row.removed:
                batch.po_total -= row.po_total
            if cases_ordered or units_ordered:
                row.cases_ordered = cases_ordered or None
                row.units_ordered = units_ordered or None
                if row.removed:
                    row.removed = False
                    batch.rowcount += 1
                self.handler.refresh_row(row)
                if row.po_unit_cost:
                    row.po_total = row.po_unit_cost * self.handler.get_units_ordered(row)
                    batch.po_total = (batch.po_total or 0) + row.po_total
            else:
                row.removed = True

        elif cases_ordered or units_ordered:
            row = model.PurchaseBatchRow()
            row.product = product
            row.cases_ordered = cases_ordered or None
            row.units_ordered = units_ordered or None
            self.handler.add_row(batch, row)
            if row.po_unit_cost:
                row.po_total = row.po_unit_cost * self.handler.get_units_ordered(row)
                batch.po_total = (batch.po_total or 0) + row.po_total

        return {
            'row_cases_ordered': '' if not row or row.removed else int(row.cases_ordered or 0),
            'row_units_ordered': '' if not row or row.removed else int(row.units_ordered or 0),
            'row_po_total': '' if not row or row.removed else '${:0,.2f}'.format(row.po_total or 0),
            'batch_po_total': '${:0,.2f}'.format(batch.po_total or 0),
        }

    def render_mobile_listitem(self, batch, i):
        return "({}) {} on {} for ${:0,.2f}".format(batch.id_str, batch.vendor,
                                                    batch.date_ordered, batch.po_total or 0)

    def mobile_create(self):
        """
        Mobile view for creating a new ordering batch
        """
        mode = self.batch_mode
        data = {'mode': mode}

        vendor = None
        if self.request.method == 'POST' and self.request.POST.get('vendor'):
            vendor = self.Session.query(model.Vendor).get(self.request.POST['vendor'])
            if vendor:

                # fetch first to avoid flush below
                store = self.rattail_config.get_store(self.Session())

                batch = self.model_class()
                batch.mode = mode
                batch.vendor = vendor
                batch.store = store
                batch.buyer = self.request.user.employee
                batch.created_by = self.request.user
                batch.po_total = 0
                kwargs = self.get_batch_kwargs(batch, mobile=True)
                batch = self.handler.make_batch(self.Session(), **kwargs)
                if self.handler.should_populate(batch):
                    self.handler.populate(batch)
                return self.redirect(self.request.route_url('mobile.ordering.view', uuid=batch.uuid))

        data['index_title'] = self.get_index_title()
        data['index_url'] = self.get_index_url(mobile=True)
        data['mode_title'] = self.enum.PURCHASE_BATCH_MODE[mode].capitalize()

        data['vendor_use_autocomplete'] = self.rattail_config.getbool(
            'rattail', 'vendor.use_autocomplete', default=True)
        if not data['vendor_use_autocomplete']:
            vendors = self.Session.query(model.Vendor)\
                                  .order_by(model.Vendor.name)
            options = [(tags.Option(vendor.name, vendor.uuid))
                       for vendor in vendors]
            options.insert(0, tags.Option("(please choose)", ''))
            data['vendor_options'] = options

        return self.render_to_response('create', data, mobile=True)

    def configure_mobile_row_form(self, f):
        super(OrderingBatchView, self).configure_mobile_row_form(f)
        if self.editing:
            # TODO: probably should take `allow_cases` into account here...
            f.focus_spec = '[name="units_ordered"]'

    def download_excel(self):
        """
        Download ordering batch as Excel spreadsheet.
        """
        batch = self.get_instance()

        # populate Excel worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Purchase Order"
        worksheet.append(["Store", "Vendor", "Date ordered"])
        worksheet.append([batch.store.name, batch.vendor.name, batch.date_ordered.strftime('%m/%d/%Y')])
        worksheet.append([])
        worksheet.append(['vendor_code', 'upc', 'brand_name', 'description', 'cases_ordered', 'units_ordered'])
        for row in batch.active_rows():
            worksheet.append([row.vendor_code, six.text_type(row.upc), row.brand_name,
                              '{} {}'.format(row.description, row.size),
                              row.cases_ordered, row.units_ordered])

        # write Excel file to batch data dir
        filedir = batch.filedir(self.rattail_config)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        filename = 'PO.{}.xlsx'.format(batch.id_str)
        path = batch.filepath(self.rattail_config, filename)
        workbook.save(path)

        return self.file_response(path)

    @classmethod
    def _ordering_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix permission group label
        config.add_tailbone_permission_group(permission_prefix, model_title_plural)

        # download as Excel
        config.add_route('{}.download_excel'.format(route_prefix), '{}/{{uuid}}/excel'.format(url_prefix))
        config.add_view(cls, attr='download_excel', route_name='{}.download_excel'.format(route_prefix),
                        permission='{}.download_excel'.format(permission_prefix))
        config.add_tailbone_permission(permission_prefix, '{}.download_excel'.format(permission_prefix),
                                       "Download {} as Excel".format(model_title))

    @classmethod
    def defaults(cls, config):
        cls._ordering_defaults(config)
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)


def includeme(config):
    OrderingBatchView.defaults(config)

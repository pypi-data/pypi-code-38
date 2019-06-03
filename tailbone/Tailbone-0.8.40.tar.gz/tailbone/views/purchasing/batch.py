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
Base views for purchasing batches
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model, api
from rattail.time import localtime

import colander
from deform import widget as dfwidget
from pyramid import httpexceptions
from webhelpers2.html import tags, HTML

from tailbone import forms, grids
from tailbone.views.batch import BatchMasterView


class PurchasingBatchView(BatchMasterView):
    """
    Master view for purchase order batches.
    """
    model_class = model.PurchaseBatch
    model_row_class = model.PurchaseBatchRow
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'
    supports_new_product = False
    cloneable = True

    labels = {
        'po_total': "PO Total",
    }

    grid_columns = [
        'id',
        'vendor',
        'department',
        'buyer',
        'date_ordered',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'store',
        'buyer',
        'vendor',
        'department',
        'purchase',
        'vendor_email',
        'vendor_fax',
        'vendor_contact',
        'vendor_phone',
        'date_ordered',
        'date_received',
        'po_number',
        'po_total',
        'invoice_date',
        'invoice_number',
        'invoice_total',
        'notes',
        'created',
        'created_by',
        'status_code',
        'complete',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'upc': "UPC",
        'item_id': "Item ID",
        'brand_name': "Brand",
        'po_line_number': "PO Line Number",
        'po_unit_cost': "PO Unit Cost",
        'po_total': "PO Total",
    }

    # row_grid_columns = [
    #     'sequence',
    #     'upc',
    #     # 'item_id',
    #     'brand_name',
    #     'description',
    #     'size',
    #     'cases_ordered',
    #     'units_ordered',
    #     'cases_received',
    #     'units_received',
    #     'po_total',
    #     'invoice_total',
    #     'credits',
    #     'status_code',
    # ]

    row_form_fields = [
        'upc',
        'item_id',
        'product',
        'brand_name',
        'description',
        'size',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'cases_received',
        'units_received',
        'cases_damaged',
        'units_damaged',
        'cases_expired',
        'units_expired',
        'cases_mispick',
        'units_mispick',
        'po_line_number',
        'po_unit_cost',
        'po_total',
        'invoice_line_number',
        'invoice_unit_cost',
        'invoice_total',
        'invoice_total_calculated',
        'status_code',
        'credits',
    ]

    mobile_row_form_fields = [
        'upc',
        'item_id',
        'product',
        'brand_name',
        'description',
        'size',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'cases_received',
        'units_received',
        'cases_damaged',
        'units_damaged',
        'cases_expired',
        'units_expired',
        'cases_mispick',
        'units_mispick',
        # 'po_line_number',
        'po_unit_cost',
        'po_total',
        # 'invoice_line_number',
        'invoice_unit_cost',
        'invoice_total',
        'status_code',
        # 'credits',
    ]

    @property
    def batch_mode(self):
        raise NotImplementedError("Please define `batch_mode` for your purchasing batch view")

    def query(self, session):
        return session.query(model.PurchaseBatch)\
                      .filter(model.PurchaseBatch.mode == self.batch_mode)

    def configure_grid(self, g):
        super(PurchasingBatchView, self).configure_grid(g)

        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

        g.joiners['department'] = lambda q: q.join(model.Department)
        g.filters['department'] = g.make_filter('department', model.Department.name)
        g.sorters['department'] = g.make_sorter(model.Department.name)

        g.joiners['buyer'] = lambda q: q.join(model.Employee).join(model.Person)
        g.filters['buyer'] = g.make_filter('buyer', model.Person.display_name,
                                           default_active=True, default_verb='contains')
        g.sorters['buyer'] = g.make_sorter(model.Person.display_name)

        if self.request.has_perm('{}.execute'.format(self.get_permission_prefix())):
            g.filters['complete'].default_active = True
            g.filters['complete'].default_verb = 'is_true'

        # invoice_total
        g.set_type('invoice_total', 'currency')
        g.set_label('invoice_total', "Total")

        # invoice_total_calculated
        g.set_type('invoice_total_calculated', 'currency')
        g.set_label('invoice_total_calculated', "Total")

        g.set_label('date_ordered', "Ordered")
        g.set_label('date_received', "Received")

    def grid_extra_class(self, batch, i):
        if batch.status_code == batch.STATUS_UNKNOWN_PRODUCT:
            return 'notice'

#     def make_form(self, batch, **kwargs):
#         if self.creating:
#             kwargs.setdefault('id', 'new-purchase-form')
#         form = super(PurchasingBatchView, self).make_form(batch, **kwargs)
#         return form

    def configure_common_form(self, f):
        super(PurchasingBatchView, self).configure_common_form(f)

        # po_total
        if self.creating:
            f.remove_field('po_total')
        else:
            f.set_readonly('po_total')
            f.set_type('po_total', 'currency')

    def configure_form(self, f):
        super(PurchasingBatchView, self).configure_form(f)
        batch = f.model_instance
        today = localtime(self.rattail_config).date()

        # mode
        f.set_enum('mode', self.enum.PURCHASE_BATCH_MODE)

        # store
        single_store = self.rattail_config.single_store()
        if self.creating:
            f.replace('store', 'store_uuid')
            if single_store:
                store = self.rattail_config.get_store(self.Session())
                f.set_widget('store_uuid', forms.widgets.ReadonlyWidget())
                f.set_default('store_uuid', store.uuid)
                f.set_hidden('store_uuid')
            else:
                f.set_widget('store_uuid', dfwidget.SelectWidget(values=self.get_store_values()))
                f.set_label('store_uuid', "Store")
        else:
            if single_store:
                f.remove_field('store')
            else:
                f.set_readonly('store')
                f.set_renderer('store', self.render_store)

        # purchase
        f.set_renderer('purchase', self.render_purchase)
        if self.editing:
            f.set_readonly('purchase')

        # vendor
        # fs.vendor.set(renderer=forms.renderers.VendorFieldRenderer,
        #               attrs={'selected': 'vendor_selected',
        #                      'cleared': 'vendor_cleared'})
        f.set_renderer('vendor', self.render_vendor)
        if self.creating:
            f.replace('vendor', 'vendor_uuid')
            f.set_label('vendor_uuid', "Vendor")
            widget_type = self.rattail_config.get('tailbone', 'default_widget.vendor',
                                                  default='autocomplete')
            if widget_type == 'autocomplete':
                vendor_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('vendor_uuid'):
                        vendor = self.Session.query(model.Vendor).get(self.request.POST['vendor_uuid'])
                        if vendor:
                            vendor_display = six.text_type(vendor)
                vendors_url = self.request.route_url('vendors.autocomplete')
                f.set_widget('vendor_uuid', forms.widgets.JQueryAutocompleteWidget(
                    field_display=vendor_display, service_url=vendors_url))
            elif widget_type == 'dropdown':
                vendors = self.Session.query(model.Vendor)\
                                      .order_by(model.Vendor.id)
                vendor_values = [(vendor.uuid, "({}) {}".format(vendor.id, vendor.name))
                                 for vendor in vendors]
                f.set_widget('vendor_uuid', dfwidget.SelectWidget(values=vendor_values))
            else:
                raise NotImplementedError("Unsupported vendor widget type: {}".format(widget_type))
        elif self.editing:
            f.set_readonly('vendor')

        # department
        f.set_renderer('department', self.render_department)
        if self.creating:
            if 'department' in f.fields:
                f.replace('department', 'department_uuid')
                f.set_node('department_uuid', colander.String())
                dept_options = self.get_department_options()
                dept_values = [(v, k) for k, v in dept_options]
                f.set_widget('department_uuid', dfwidget.SelectWidget(values=dept_values))
                f.set_label('department_uuid', "Department")
        else:
            f.set_readonly('department')

        # buyer
        if 'buyer' in f:
            f.set_renderer('buyer', self.render_buyer)
            if self.creating or self.editing:
                f.replace('buyer', 'buyer_uuid')
                f.set_node('buyer_uuid', colander.String(), missing=colander.null)
                buyer_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('buyer_uuid'):
                        buyer = self.Session.query(model.Employee).get(self.request.POST['buyer_uuid'])
                        if buyer:
                            buyer_display = six.text_type(buyer)
                elif self.creating:
                    buyer = self.request.user.employee
                    buyer_display = six.text_type(buyer)
                    f.set_default('buyer_uuid', buyer.uuid)
                elif self.editing:
                    buyer_display = six.text_type(batch.buyer or '')
                buyers_url = self.request.route_url('employees.autocomplete')
                f.set_widget('buyer_uuid', forms.widgets.JQueryAutocompleteWidget(
                    field_display=buyer_display, service_url=buyers_url))
                f.set_label('buyer_uuid', "Buyer")

        # date_ordered
        f.set_type('date_ordered', 'date_jquery')
        if self.creating:
            f.set_default('date_ordered', today)

        # date_received
        f.set_type('date_received', 'date_jquery')
        if self.creating:
            f.set_default('date_received', today)

        # invoice_date
        f.set_type('invoice_date', 'date_jquery')

        # po_number
        f.set_label('po_number', "PO Number")

        # invoice_total
        f.set_readonly('invoice_total')
        f.set_type('invoice_total', 'currency')

        # invoice_total_calculated
        f.set_readonly('invoice_total_calculated')
        f.set_type('invoice_total_calculated', 'currency')

        # vendor_email
        f.set_readonly('vendor_email')
        f.set_renderer('vendor_email', self.render_vendor_email)

        # vendor_fax
        f.set_readonly('vendor_fax')
        f.set_renderer('vendor_fax', self.render_vendor_fax)

        # vendor_contact
        f.set_readonly('vendor_contact')
        f.set_renderer('vendor_contact', self.render_vendor_contact)

        # vendor_phone
        f.set_readonly('vendor_phone')
        f.set_renderer('vendor_phone', self.render_vendor_phone)

        if self.creating:
            f.remove_fields('po_total',
                            'invoice_total',
                            'complete',
                            'vendor_email',
                            'vendor_fax',
                            'vendor_phone',
                            'vendor_contact',
                            'status_code')

    def render_store(self, batch, field):
        store = batch.store
        if not store:
            return ""
        text = "({}) {}".format(store.id, store.name)
        url = self.request.route_url('stores.view', uuid=store.uuid)
        return tags.link_to(text, url)

    def render_purchase(self, batch, field):
        purchase = batch.purchase
        if not purchase:
            return ""
        text = six.text_type(purchase)
        url = self.request.route_url('purchases.view', uuid=purchase.uuid)
        return tags.link_to(text, url)

    def render_vendor(self, batch, field):
        vendor = batch.vendor
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def render_vendor_email(self, batch, field):
        if batch.vendor.email:
            return batch.vendor.email.address

    def render_vendor_fax(self, batch, field):
        return self.get_vendor_fax_number(batch)

    def render_vendor_contact(self, batch, field):
        if batch.vendor.contact:
            return six.text_type(batch.vendor.contact)

    def render_vendor_phone(self, batch, field):
        return self.get_vendor_phone_number(batch)

    def render_department(self, batch, field):
        department = batch.department
        if not department:
            return ""
        if department.number:
            text = "({}) {}".format(department.number, department.name)
        else:
            text = department.name
        url = self.request.route_url('departments.view', uuid=department.uuid)
        return tags.link_to(text, url)

    def render_buyer(self, batch, field):
        employee = batch.buyer
        if not employee:
            return ""
        text = six.text_type(employee)
        if self.request.has_perm('employees.view'):
            url = self.request.route_url('employees.view', uuid=employee.uuid)
            return tags.link_to(text, url)
        return text

    def get_store_values(self):
        stores = self.Session.query(model.Store)\
                             .order_by(model.Store.id)
        return [(s.uuid, "({}) {}".format(s.id, s.name))
                for s in stores]

    def get_vendors(self):
        return self.Session.query(model.Vendor)\
                           .order_by(model.Vendor.name)

    def get_vendor_values(self):
        vendors = self.get_vendors()
        return [(v.uuid, "({}) {}".format(v.id, v.name))
                for v in vendors]

    def get_vendor_values(self):
        vendors = self.get_vendors()
        return [(v.uuid, "({}) {}".format(v.id, v.name))
                for v in vendors]

    def get_buyers(self):
        return self.Session.query(model.Employee)\
                           .join(model.Person)\
                           .filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)\
                           .order_by(model.Person.display_name)

    def get_buyer_values(self):
        buyers = self.get_buyers()
        return [(b.uuid, six.text_type(b))
                for b in buyers]

    def get_department_options(self):
        departments = self.Session.query(model.Department).order_by(model.Department.number)
        return [('{} {}'.format(d.number, d.name), d.uuid) for d in departments]

    def get_vendor_phone_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Voice':
                return phone.number

    def get_vendor_fax_number(self, batch):
        for phone in batch.vendor.phones:
            if phone.type == 'Fax':
                return phone.number

    def eligible_purchases(self, vendor_uuid=None, mode=None):
        if not vendor_uuid:
            vendor_uuid = self.request.GET.get('vendor_uuid')
        vendor = self.Session.query(model.Vendor).get(vendor_uuid) if vendor_uuid else None
        if not vendor:
            return {'error': "Must specify a vendor."}

        if mode is None:
            mode = self.request.GET.get('mode')
            mode = int(mode) if mode and mode.isdigit() else None
        if not mode or mode not in self.enum.PURCHASE_BATCH_MODE:
            return {'error': "Unknown mode: {}".format(mode)}

        purchases = self.Session.query(model.Purchase)\
                                .filter(model.Purchase.vendor == vendor)
        if mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_ORDERED)\
                                 .order_by(model.Purchase.date_ordered, model.Purchase.created)
        elif mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_RECEIVED)\
                                 .order_by(model.Purchase.date_received, model.Purchase.created)

        return {'purchases': [{'key': p.uuid,
                               'department_uuid': p.department_uuid or '',
                               'display': self.render_eligible_purchase(p)}
                              for p in purchases]}

    def render_eligible_purchase(self, purchase):
        if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
            date = purchase.date_ordered
            total = purchase.po_total
        elif purchase.status == self.enum.PURCHASE_STATUS_RECEIVED:
            date = purchase.date_received
            total = purchase.invoice_total
        return '{} for ${:0,.2f} ({})'.format(date, total, purchase.department or purchase.buyer)

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(PurchasingBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        kwargs['mode'] = self.batch_mode
        kwargs['truck_dump'] = batch.truck_dump
        kwargs['invoice_parser_key'] = batch.invoice_parser_key

        if batch.store:
            kwargs['store'] = batch.store
        elif batch.store_uuid:
            kwargs['store_uuid'] = batch.store_uuid

        if batch.truck_dump_batch:
            kwargs['truck_dump_batch'] = batch.truck_dump_batch
        elif batch.truck_dump_batch_uuid:
            kwargs['truck_dump_batch_uuid'] = batch.truck_dump_batch_uuid

        if batch.vendor:
            kwargs['vendor'] = batch.vendor
        elif batch.vendor_uuid:
            kwargs['vendor_uuid'] = batch.vendor_uuid

        if batch.department:
            kwargs['department'] = batch.department
        elif batch.department_uuid:
            kwargs['department_uuid'] = batch.department_uuid

        if batch.buyer:
            kwargs['buyer'] = batch.buyer
        elif batch.buyer_uuid:
            kwargs['buyer_uuid'] = batch.buyer_uuid

        kwargs['po_number'] = batch.po_number
        kwargs['po_total'] = batch.po_total

        # TODO: should these always get set?
        if self.batch_mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            kwargs['date_ordered'] = batch.date_ordered
        elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            kwargs['date_ordered'] = batch.date_ordered
            kwargs['date_received'] = batch.date_received
            kwargs['invoice_number'] = batch.invoice_number
        elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            kwargs['invoice_date'] = batch.invoice_date
            kwargs['invoice_number'] = batch.invoice_number

        if self.batch_mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                               self.enum.PURCHASE_BATCH_MODE_COSTING):
            purchase = batch.purchase
            if not purchase and batch.purchase_uuid:
                purchase = self.Session.query(model.Purchase).get(batch.purchase_uuid)
                assert purchase
            if purchase:
                kwargs['purchase'] = purchase
                kwargs['buyer'] = purchase.buyer
                kwargs['buyer_uuid'] = purchase.buyer_uuid
                kwargs['date_ordered'] = purchase.date_ordered
                kwargs['po_total'] = purchase.po_total

        return kwargs

#     def template_kwargs_view(self, **kwargs):
#         kwargs = super(PurchasingBatchView, self).template_kwargs_view(**kwargs)
#         vendor = kwargs['batch'].vendor
#         kwargs['vendor_cost_count'] = Session.query(model.ProductCost)\
#                                              .filter(model.ProductCost.vendor == vendor)\
#                                              .count()
#         kwargs['vendor_cost_threshold'] = self.rattail_config.getint(
#             'tailbone', 'purchases.order_form.vendor_cost_warning_threshold', default=699)
#         return kwargs

    def template_kwargs_create(self, **kwargs):
        kwargs['purchases_field'] = 'purchase_uuid'
        return kwargs

#     def get_row_data(self, batch):
#         query = super(PurchasingBatchView, self).get_row_data(batch)
#         return query.options(orm.joinedload(model.PurchaseBatchRow.credits))

    def sort_mobile_row_data(self, query):
        return query.order_by(model.PurchaseBatchRow.modified.desc())

    def configure_row_grid(self, g):
        super(PurchasingBatchView, self).configure_row_grid(g)

        g.set_type('upc', 'gpc')
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')
        g.set_type('cases_shipped', 'quantity')
        g.set_type('units_shipped', 'quantity')
        g.set_type('cases_received', 'quantity')
        g.set_type('units_received', 'quantity')
        g.set_type('po_total', 'currency')
        g.set_type('credits', 'boolean')

        # we only want the grid column to have abbreviated label, but *not* the filter
        # TODO: would be nice to somehow make this simpler
        g.set_label('cases_ordered', "Cases Ord.")
        g.filters['cases_ordered'].label = "Cases Ordered"
        g.set_label('units_ordered', "Units Ord.")
        g.filters['units_ordered'].label = "Units Ordered"
        g.set_label('cases_shipped', "Cases Shp.")
        g.filters['cases_shipped'].label = "Cases Shipped"
        g.set_label('units_shipped', "Units Shp.")
        g.filters['units_shipped'].label = "Units Shipped"
        g.set_label('cases_received', "Cases Rec.")
        g.filters['cases_received'].label = "Cases Received"
        g.set_label('units_received', "Units Rec.")
        g.filters['units_received'].label = "Units Received"

        # invoice_total
        g.set_type('invoice_total', 'currency')
        g.set_label('invoice_total', "Total")

        # invoice_total_calculated
        g.set_type('invoice_total_calculated', 'currency')
        g.set_label('invoice_total_calculated', "Total")

        g.set_label('po_total', "Total")
        g.set_label('credits', "Credits?")

    def make_row_grid_tools(self, batch):
        return self.make_default_row_grid_tools(batch)

    def row_grid_extra_class(self, row, i):
        if row.status_code in (row.STATUS_PRODUCT_NOT_FOUND,
                               row.STATUS_COST_NOT_FOUND):
            return 'warning'
        if row.status_code in (row.STATUS_INCOMPLETE,
                               row.STATUS_CASE_QUANTITY_DIFFERS,
                               row.STATUS_ORDERED_RECEIVED_DIFFER,
                               row.STATUS_TRUCKDUMP_UNCLAIMED,
                               row.STATUS_TRUCKDUMP_PARTCLAIMED,
                               row.STATUS_OUT_OF_STOCK):
            return 'notice'

    def configure_row_form(self, f):
        super(PurchasingBatchView, self).configure_row_form(f)
        row = f.model_instance
        if self.creating:
            batch = self.get_instance()
        else:
            batch = self.get_parent(row)

        # readonly fields
        f.set_readonly('case_quantity')

        # quantity fields
        f.set_type('case_quantity', 'quantity')
        f.set_type('cases_ordered', 'quantity')
        f.set_type('units_ordered', 'quantity')
        f.set_type('cases_shipped', 'quantity')
        f.set_type('units_shipped', 'quantity')
        f.set_type('cases_received', 'quantity')
        f.set_type('units_received', 'quantity')
        f.set_type('cases_damaged', 'quantity')
        f.set_type('units_damaged', 'quantity')
        f.set_type('cases_expired', 'quantity')
        f.set_type('units_expired', 'quantity')
        f.set_type('cases_mispick', 'quantity')
        f.set_type('units_mispick', 'quantity')

        # currency fields
        f.set_type('po_unit_cost', 'currency')
        f.set_type('po_total', 'currency')
        f.set_type('invoice_unit_cost', 'currency')

        # upc
        f.set_type('upc', 'gpc')

        # invoice total
        f.set_readonly('invoice_total')
        f.set_type('invoice_total', 'currency')
        f.set_label('invoice_total', "Invoice Total (Orig.)")

        # invoice total_calculated
        f.set_readonly('invoice_total_calculated')
        f.set_type('invoice_total_calculated', 'currency')
        f.set_label('invoice_total_calculated', "Invoice Total (Calc.)")

        # credits
        f.set_readonly('credits')
        f.set_renderer('credits', self.render_row_credits)

        if self.creating:
            f.remove_fields(
                'upc',
                'product',
                'po_total',
                'invoice_total',
            )
            if self.batch_mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
                f.remove_fields('cases_received',
                                'units_received')
            elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                f.remove_fields('cases_ordered',
                                'units_ordered')

        elif self.editing:
            f.set_readonly('upc')
            f.set_readonly('item_id')
            f.set_readonly('product')
            f.set_renderer('product', self.render_product)

            # TODO: what's up with this again?
            # f.remove_fields('po_total',
            #                 'invoice_total',
            #                 'status_code')

        elif self.viewing:
            if row.product:
                f.remove_fields('brand_name',
                                'description',
                                'size')
                f.set_renderer('product', self.render_product)
            else:
                f.remove_field('product')

    def render_row_credits(self, row, field):
        if not row.credits:
            return ""

        route_prefix = self.get_route_prefix()
        columns = [
            'credit_type',
            'cases_shorted',
            'units_shorted',
            'credit_total',
        ]
        g = grids.Grid(
            key='{}.row_credits'.format(route_prefix),
            data=row.credits,
            columns=columns,
            labels={'credit_type': "Type",
                    'cases_shorted': "Cases",
                    'units_shorted': "Units"})
        g.set_type('cases_shorted', 'quantity')
        g.set_type('units_shorted', 'quantity')
        g.set_type('credit_total', 'currency')
        return HTML.literal(g.render_grid())

    def configure_mobile_row_form(self, f):
        super(PurchasingBatchView, self).configure_mobile_row_form(f)
        # row = f.model_instance
        # if self.creating:
        #     batch = self.get_instance()
        # else:
        #     batch = self.get_parent(row)

        # # readonly fields
        # f.set_readonly('case_quantity')
        # f.set_readonly('credits')

        # quantity fields
        f.set_type('case_quantity', 'quantity')
        f.set_type('cases_ordered', 'quantity')
        f.set_type('units_ordered', 'quantity')
        f.set_type('cases_received', 'quantity')
        f.set_type('units_received', 'quantity')
        f.set_type('cases_damaged', 'quantity')
        f.set_type('units_damaged', 'quantity')
        f.set_type('cases_expired', 'quantity')
        f.set_type('units_expired', 'quantity')
        f.set_type('cases_mispick', 'quantity')
        f.set_type('units_mispick', 'quantity')

        # currency fields
        f.set_type('po_unit_cost', 'currency')
        f.set_type('po_total', 'currency')
        f.set_type('invoice_unit_cost', 'currency')
        f.set_type('invoice_total', 'currency')

        # if self.creating:
        #     f.remove_fields(
        #         'upc',
        #         'product',
        #         'po_total',
        #         'invoice_total',
        #     )
        #     if self.batch_mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
        #         f.remove_fields('cases_received',
        #                         'units_received')
        #     elif self.batch_mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
        #         f.remove_fields('cases_ordered',
        #                         'units_ordered')

        # elif self.editing:
        #     f.set_readonly('upc')
        #     f.set_readonly('product')
        #     f.remove_fields('po_total',
        #                     'invoice_total',
        #                     'status_code')

        # elif self.viewing:
        #     if row.product:
        #         f.remove_fields('brand_name',
        #                         'description',
        #                         'size')
        #     else:
        #         f.remove_field('product')

    def mobile_new_product(self):
        """
        View which allows user to create a new Product and add a row for it to
        the Purchasing Batch.
        """
        batch = self.get_instance()
        batch_url = self.get_action_url('view', batch, mobile=True)
        form = forms.Form(schema=self.make_new_product_schema(),
                          request=self.request,
                          mobile=True,
                          cancel_url=batch_url)

        if form.validate(newstyle=True):
            product = model.Product()
            product.item_id = form.validated['item_id']
            product.description = form.validated['description']
            row = self.model_row_class()
            row.product = product
            self.handler.add_row(batch, row)
            self.Session.flush()
            return self.redirect(self.get_row_action_url('edit', row, mobile=True))

        return self.render_to_response('new_product', {
            'form': form,
            'dform': form.make_deform_form(),
            'instance_title': self.get_instance_title(batch),
            'instance_url': batch_url,
        }, mobile=True)

    def make_new_product_schema(self):
        """
        Must return a ``colander.Schema`` instance for use with the form in the
        :meth:`mobile_new_product()` view.
        """
        return NewProduct()

#     def item_lookup(self, value, field=None):
#         """
#         Try to locate a single product using ``value`` as a lookup code.
#         """
#         batch = self.get_instance()
#         product = api.get_product_by_vendor_code(Session(), value, vendor=batch.vendor)
#         if product:
#             return product.uuid
#         if value.isdigit():
#             product = api.get_product_by_upc(Session(), GPC(value))
#             if not product:
#                 product = api.get_product_by_upc(Session(), GPC(value, calc_check_digit='upc'))
#             if product:
#                 if not product.cost_for_vendor(batch.vendor):
#                     raise fa.ValidationError("Product {} exists but has no cost for vendor {}".format(
#                         product.upc.pretty(), batch.vendor))
#                 return product.uuid
#         raise fa.ValidationError("Product not found")

#     def before_create_row(self, form):
#         row = form.fieldset.model
#         batch = self.get_instance()
#         batch.add_row(row)
#         # TODO: this seems heavy-handed but works..
#         row.product_uuid = self.item_lookup(form.fieldset.item_lookup.value)

#     def after_create_row(self, row):
#         self.handler.refresh_row(row)

    def save_edit_row_form(self, form):
        row = form.model_instance
        batch = row.batch

        # first undo any totals previously in effect for the row
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING and row.po_total:
            batch.po_total -= row.po_total
        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING and row.invoice_total:
            batch.invoice_total -= row.invoice_total

        row = super(PurchasingBatchView, self).save_edit_row_form(form)
        # TODO: is this needed?
        # self.handler.refresh_row(row)
        return row

#     def redirect_after_create_row(self, row):
#         self.request.session.flash("Added item: {} {}".format(row.upc.pretty(), row.product))
#         return self.redirect(self.request.current_route_url())

    # TODO: seems like this should be master behavior, controlled by setting?
    def redirect_after_edit_row(self, row, mobile=False):
        parent = self.get_parent(row)
        return self.redirect(self.get_action_url('view', parent, mobile=mobile))

#     def get_execute_success_url(self, batch, result, **kwargs):
#         # if batch execution yielded a Purchase, redirect to it
#         if isinstance(result, model.Purchase):
#             return self.request.route_url('purchases.view', uuid=result.uuid)

#         # otherwise just view batch again
#         return self.get_action_url('view', batch)


    @classmethod
    def _purchasing_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # eligible purchases (AJAX)
        config.add_route('{}.eligible_purchases'.format(route_prefix), '{}/eligible-purchases'.format(url_prefix))
        config.add_view(cls, attr='eligible_purchases', route_name='{}.eligible_purchases'.format(route_prefix),
                        renderer='json', permission='{}.view'.format(permission_prefix))

        # add new product
        if cls.supports_new_product:
            config.add_tailbone_permission(permission_prefix, '{}.new_product'.format(permission_prefix),
                                           "Create new Product when adding row to {}".format(model_title))
            config.add_route('mobile.{}.new_product'.format(route_prefix), '{}/{{{}}}/new-product'.format(url_prefix, model_key))
            config.add_view(cls, attr='mobile_new_product', route_name='mobile.{}.new_product'.format(route_prefix),
                            permission='{}.new_product'.format(permission_prefix))


    @classmethod
    def defaults(cls, config):
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)


class NewProduct(colander.Schema):

    item_id = colander.SchemaNode(colander.String())

    description = colander.SchemaNode(colander.String())

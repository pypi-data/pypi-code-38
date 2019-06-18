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
Views for "true" purchase orders
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from webhelpers2.html import HTML, tags

from tailbone.db import Session
from tailbone.views import MasterView


class PurchaseView(MasterView):
    """
    Master view for purchase orders.
    """
    model_class = model.Purchase
    creatable = False
    editable = False

    has_rows = True
    model_row_class = model.PurchaseItem
    row_model_title = 'Purchase Item'

    grid_columns = [
        'store',
        'vendor',
        'department',
        'buyer',
        'date_ordered',
        'date_received',
        'invoice_number',
        'status',
    ]

    form_fields = [
        'store',
        'vendor',
        'department',
        'status',
        'buyer',
        'date_ordered',
        'date_received',
        'po_number',
        'po_total',
        'ship_method',
        'notes_to_vendor',
        'invoice_date',
        'invoice_number',
        'invoice_total',
        'created',
        'created_by',
        'batches',
    ]

    row_labels = {
        'vendor_code': "Vendor Item Code",
        'upc': "UPC",
        'po_unit_cost': "PO Unit Cost",
        'po_total': "PO Total",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'item_id',
        'brand_name',
        'description',
        'size',
        'cases_ordered',
        'units_ordered',
        'cases_received',
        'units_received',
        'po_total',
        'invoice_total',
    ]

    row_form_fields = [
        'sequence',
        'vendor_code',
        'upc',
        'product',
        'department',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'cases_received',
        'units_received',
        'cases_damaged',
        'units_damaged',
        'cases_expired',
        'units_expired',
        'po_unit_cost',
        'po_total',
        'invoice_unit_cost',
        'invoice_total',
    ]

    def get_instance_title(self, purchase):
        if purchase.status >= self.enum.PURCHASE_STATUS_COSTED:
            if purchase.invoice_date:
                return "{} (invoiced {})".format(purchase.vendor, purchase.invoice_date.strftime('%Y-%m-%d'))
            if purchase.date_received:
                return "{} (invoiced {})".format(purchase.vendor, purchase.date_received.strftime('%Y-%m-%d'))
            return "{} (invoiced)".format(purchase.vendor)
        elif purchase.status >= self.enum.PURCHASE_STATUS_RECEIVED:
            if purchase.date_received:
                return "{} (received {})".format(purchase.vendor, purchase.date_received.strftime('%Y-%m-%d'))
            return "{} (received)".format(purchase.vendor)
        elif purchase.status >= self.enum.PURCHASE_STATUS_ORDERED:
            if purchase.date_ordered:
                return "{} (ordered {})".format(purchase.vendor, purchase.date_ordered.strftime('%Y-%m-%d'))
            return "{} (ordered)".format(purchase.vendor)
        return six.text_type(purchase)

    def configure_grid(self, g):
        super(PurchaseView, self).configure_grid(g)

        g.joiners['store'] = lambda q: q.join(model.Store)
        g.filters['store'] = g.make_filter('store', model.Store.name)
        g.sorters['store'] = g.make_sorter(model.Store.name)

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

        # date_ordered
        g.filters['date_ordered'].default_active = True
        g.filters['date_ordered'].default_verb = 'equal'
        g.set_label('date_ordered', "Ordered")
        g.set_sort_defaults('date_ordered', 'desc')

        # date_received
        g.filters['date_received'].default_active = True
        g.filters['date_received'].default_verb = 'equal'
        g.set_label('date_received', "Received")

        # status
        g.set_enum('status', self.enum.PURCHASE_STATUS)
        g.filters['status'].default_active = True
        g.filters['status'].verbs = ['equal', 'not_equal', 'is_any']
        g.filters['status'].default_verb = 'is_any'

        g.set_label('invoice_number', "Invoice No.")

    def configure_form(self, f):
        super(PurchaseView, self).configure_form(f)

        f.set_renderer('store', self.render_store)
        f.set_renderer('vendor', self.render_vendor)
        f.set_renderer('department', self.render_department)

        f.set_readonly('status')
        f.set_enum('status', self.enum.PURCHASE_STATUS)

        f.set_label('po_number', "PO Number")
        f.set_label('po_total', "PO Total")
        f.set_type('po_total', 'currency')

        f.set_type('invoice_total', 'currency')

        f.set_renderer('batches', self.render_batches)

        if self.viewing:
            purchase = f.model_instance
            if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
                f.remove('date_received',
                         'invoice_number',
                         'invoice_total')

    def render_store(self, purchase, field):
        store = purchase.store
        if not store:
            return ""
        text = "({}) {}".format(store.id, store.name)
        url = self.request.route_url('stores.view', uuid=store.uuid)
        return tags.link_to(text, url)

    def render_vendor(self, purchase, field):
        vendor = purchase.vendor
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def render_department(self, purchase, field):
        department = purchase.department
        if not department:
            return ""
        if department.number:
            text = "({}) {}".format(department.number, department.name)
        else:
            text = department.name
        url = self.request.route_url('departments.view', uuid=department.uuid)
        return tags.link_to(text, url)

    def render_batches(self, purchase, field):
        batches = purchase.batches
        if not batches:
            return ""

        routes = {
            self.enum.PURCHASE_BATCH_MODE_ORDERING: 'ordering.view',
            self.enum.PURCHASE_BATCH_MODE_RECEIVING: 'receiving.view',
        }

        def render(batch):
            if batch.executed:
                actor = batch.executed_by
                pending = ''
            else:
                actor = batch.created_by
                pending = ' (pending)'
            text = '{} ({} by {}){}'.format(batch.id_str,
                                            self.enum.PURCHASE_BATCH_MODE[batch.mode],
                                            actor, pending)
            url = self.request.route_url(routes[batch.mode], uuid=batch.uuid)
            return tags.link_to(text, url)

        items = [HTML.tag('li', c=[render(batch)]) for batch in batches]
        return HTML.tag('ul', c=items)

    def delete_instance(self, purchase):
        """
        Delete all batches for the purchase, then delete the purchase.
        """
        for batch in list(purchase.batches):
            self.Session.delete(batch)
        self.Session.flush()
        self.Session.delete(purchase)
        self.Session.flush()

    def get_parent(self, item):
        return item.purchase

    def get_row_data(self, purchase):
        return Session.query(model.PurchaseItem)\
                      .filter(model.PurchaseItem.purchase == purchase)

    def configure_row_grid(self, g):
        super(PurchaseView, self).configure_row_grid(g)

        g.set_sort_defaults('sequence')

        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')
        g.set_type('cases_received', 'quantity')
        g.set_type('units_received', 'quantity')
        g.set_type('po_total', 'currency')
        g.set_type('invoice_total', 'currency')

        g.set_label('sequence', "Seq")
        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('cases_ordered', "Cases Ord.")
        g.set_label('units_ordered', "Units Ord.")
        g.set_label('cases_received', "Cases Rec.")
        g.set_label('units_received', "Units Rec.")
        g.set_label('po_total', "Total")
        g.set_label('invoice_total', "Total")

        purchase = self.get_instance()
        if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
            g.hide_column('cases_received')
            g.hide_column('units_received')
            g.hide_column('invoice_total')
        elif purchase.status in (self.enum.PURCHASE_STATUS_RECEIVED,
                                 self.enum.PURCHASE_STATUS_COSTED):
            g.hide_column('po_total')

    def configure_row_form(self, f):
        super(PurchaseView, self).configure_row_form(f)

        # currency fields
        f.set_type('po_unit_cost', 'currency')
        f.set_type('po_total', 'currency')
        f.set_type('invoice_unit_cost', 'currency')
        f.set_type('invoice_total', 'currency')

        # department
        f.set_renderer('department', self.render_row_department)

        # product
        f.set_renderer('product', self.render_product)

    def render_row_department(self, row, field):
        return "{} {}".format(row.department_number, row.department_name)

    def receiving_worksheet(self):
        purchase = self.get_instance()
        return self.render_to_response('receiving_worksheet', {
            'purchase': purchase,
        })

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        cls._defaults(config)

        # receiving worksheet
        config.add_tailbone_permission(permission_prefix, '{}.receiving_worksheet'.format(permission_prefix),
                                       "Print receiving worksheet for {}".format(model_title))
        config.add_route('{}.receiving_worksheet'.format(route_prefix), '{}/{{{}}}/receiving-worksheet'.format(url_prefix, model_key))
        config.add_view(cls, attr='receiving_worksheet', route_name='{}.receiving_worksheet'.format(route_prefix),
                        permission='{}.receiving_worksheet'.format(permission_prefix))
        


def includeme(config):
    PurchaseView.defaults(config)

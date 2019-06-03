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
Views for "true" purchase credits
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from webhelpers2.html import tags

from tailbone import grids
from tailbone.views import MasterView


class PurchaseCreditView(MasterView):
    """
    Master view for purchase credits
    """
    model_class = model.PurchaseCredit
    route_prefix = 'purchases.credits'
    url_prefix = '/purchases/credits'
    creatable = False
    editable = False
    checkboxes = True

    labels = {
        'upc': "UPC",
        'mispick_upc': "Mispick UPC",
    }

    grid_columns = [
        'vendor',
        'invoice_number',
        'invoice_date',
        'upc',
        'vendor_item_code',
        'brand_name',
        'description',
        'size',
        'cases_shorted',
        'units_shorted',
        'credit_total',
        'credit_type',
        'mispick_upc',
        'date_received',
        'status',
    ]

    form_fields = [
        'store',
        'vendor',
        'invoice_number',
        'invoice_date',
        'date_ordered',
        'date_shipped',
        'date_received',
        'department_number',
        'department_name',
        'vendor_item_code',
        'upc',
        'product',
        'case_quantity',
        'credit_type',
        'cases_shorted',
        'units_shorted',
        'invoice_line_number',
        'invoice_case_cost',
        'invoice_unit_cost',
        'invoice_total',
        'credit_total',
        'mispick_upc',
        'mispick_product',
        'product_discarded',
        'expiration_date',
        'status',
    ]

    def configure_grid(self, g):
        super(PurchaseCreditView, self).configure_grid(g)

        g.set_joiner('vendor', lambda q: q.outerjoin(model.Vendor))
        g.set_sorter('vendor', model.Vendor.name)

        g.set_sort_defaults('date_received', 'desc')

        g.set_enum('status', self.enum.PURCHASE_CREDIT_STATUS)
        g.filters['status'].set_value_renderer(grids.filters.EnumValueRenderer(self.enum.PURCHASE_CREDIT_STATUS))
        g.filters['status'].default_active = True
        g.filters['status'].default_verb = 'not_equal'
        # TODO: should not have to convert value to string!
        g.filters['status'].default_value = six.text_type(self.enum.PURCHASE_CREDIT_STATUS_SATISFIED)

        # g.set_type('upc', 'gpc')
        g.set_type('cases_shorted', 'quantity')
        g.set_type('units_shorted', 'quantity')
        g.set_type('credit_total', 'currency')

        g.set_label('invoice_number', "Invoice No.")
        g.set_label('vendor_item_code', "Item Code")
        g.set_label('brand_name', "Brand")
        g.set_label('cases_shorted', "Cases")
        g.set_label('units_shorted', "Units")
        g.set_label('credit_type', "Type")
        g.set_label('date_received', "Date")

        g.set_link('upc')
        g.set_link('vendor_item_code')
        g.set_link('brand_name')
        g.set_link('description')

    def configure_form(self, f):
        super(PurchaseCreditView, self).configure_form(f)

        # status
        f.set_enum('status', self.enum.PURCHASE_CREDIT_STATUS)

    def change_status(self):
        if self.request.method != 'POST':
            self.request.session.flash("Sorry, you must POST to change credit status", 'error')
            return self.redirect(self.get_index_url())

        status = self.request.POST.get('status', '')
        if status.isdigit():
            status = int(status)
        else:
            self.request.session.flash("Received invalid status: {}".format(status), 'error')
            return self.redirect(self.get_index_url())

        credits_ = []
        for uuid in self.request.POST.get('uuids', '').split(','):
            uuid = uuid.strip()
            if uuid:
                credit = self.Session.query(model.PurchaseCredit).get(uuid)
                if credit:
                    credits_.append(credit)
        if not credits_:
            self.request.session.flash("Received zero valid credits", 'error')
            return self.redirect(self.get_index_url())

        # okay, really change status
        for credit in credits_:
            credit.status = status

        self.request.session.flash("Changed status for {} credits".format(len(credits_)))
        return self.redirect(self.get_index_url())

    def template_kwargs_index(self, **kwargs):
        kwargs['status_options'] = self.status_options()
        return kwargs

    def status_options(self):
        options = []
        for value in sorted(self.enum.PURCHASE_CREDIT_STATUS):
            options.append(tags.Option(self.enum.PURCHASE_CREDIT_STATUS[value], value))
        return options

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # change status
        config.add_tailbone_permission(permission_prefix, '{}.change_status'.format(permission_prefix),
                                       "Change status for {}".format(model_title_plural))
        config.add_route('{}.change_status'.format(route_prefix), '{}/change-status'.format(url_prefix))
        config.add_view(cls, attr='change_status', route_name='{}.change_status'.format(route_prefix),
                        permission='{}.change_status'.format(permission_prefix))

        cls._defaults(config)


def includeme(config):
    PurchaseCreditView.defaults(config)

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
Vendor Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from webhelpers2.html import tags

from tailbone.views import MasterView, AutocompleteView


class VendorsView(MasterView):
    """
    Master view for the Vendor class.
    """
    model_class = model.Vendor
    has_versions = True

    labels = {
        'id': "ID",
        'default_phone': "Phone Number",
        'default_email': "Default Email",
    }

    grid_columns = [
        'id',
        'name',
        'abbreviation',
        'phone',
        'email',
        'contact',
    ]

    form_fields = [
        'id',
        'name',
        'abbreviation',
        'special_discount',
        'lead_time_days',
        'order_interval_days',
        'default_phone',
        'default_email',
        'orders_email',
        'contact',
    ]

    def configure_grid(self, g):
        super(VendorsView, self).configure_grid(g)

        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')

        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")

        g.set_link('id')
        g.set_link('name')
        g.set_link('abbreviation')

    def configure_form(self, f):
        super(VendorsView, self).configure_form(f)
        vendor = f.model_instance

        f.set_label('lead_time_days', "Lead Time in Days")

        f.set_label('order_interval', "Order Interval in Days")

        # default_phone
        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and vendor.phones:
            f.set_default('default_phone', vendor.phones[0].number)

        # default_email
        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and vendor.emails:
            f.set_default('default_email', vendor.emails[0].address)

        # orders_email
        f.set_renderer('orders_email', self.render_orders_email)
        if not self.creating and vendor.emails:
            f.set_default('orders_email', vendor.get_email_address(type_='Orders') or '')

        # contact
        if self.creating:
            f.remove_field('contact')
        else:
            f.set_readonly('contact')
            f.set_renderer('contact', self.render_contact)

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        vendor = super(VendorsView, self).objectify(form, data)
        vendor = self.objectify_contact(vendor, data)

        if 'orders_email' in data:
            address = data['orders_email']
            email = vendor.get_email(type_='Orders')
            if address:
                if email:
                    if email.address != address:
                        email.address = address
                else:
                    vendor.add_email_address(address, type='Orders')
            elif email:
                vendor.emails.remove(email)

        return vendor

    def render_default_email(self, vendor, field):
        if vendor.emails:
            return vendor.emails[0].address

    def render_orders_email(self, vendor, field):
        return vendor.get_email_address(type_='Orders')

    def render_default_phone(self, vendor, field):
        if vendor.phones:
            return vendor.phones[0].number

    def render_contact(self, vendor, field):
        person = vendor.contact
        if not person:
            return ""
        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def before_delete(self, vendor):
        # Remove all product costs.
        q = self.Session.query(model.ProductCost).filter(
            model.ProductCost.vendor == vendor)
        for cost in q:
            self.Session.delete(cost)

    def get_version_child_classes(self):
        return [
            (model.VendorPhoneNumber, 'parent_uuid'),
            (model.VendorEmailAddress, 'parent_uuid'),
            (model.VendorContact, 'vendor_uuid'),
        ]


class VendorsAutocomplete(AutocompleteView):

    mapped_class = model.Vendor
    fieldname = 'name'


def includeme(config):

    # autocomplete
    config.add_route('vendors.autocomplete', '/vendors/autocomplete')
    config.add_view(VendorsAutocomplete, route_name='vendors.autocomplete',
                    renderer='json', permission='vendors.list')

    VendorsView.defaults(config)

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
Customer order item views
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
from sqlalchemy import orm

from rattail.db import model
from rattail.time import localtime

from webhelpers2.html import tags

from tailbone.views import MasterView
from tailbone.util import raw_datetime


class CustomerOrderItemsView(MasterView):
    """
    Master view for customer order items
    """
    model_class = model.CustomerOrderItem
    route_prefix = 'custorders.items'
    url_prefix = '/custorders/items'
    creatable = False
    editable = False
    deletable = False

    grid_columns = [
        'person',
        'product_brand',
        'product_description',
        'product_size',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'order_created',
        'status_code',
    ]

    has_rows = True
    model_row_class = model.CustomerOrderItemEvent
    rows_title = "Event History"
    rows_filterable = False
    rows_sortable = False
    rows_pageable = False
    rows_viewable = False

    row_grid_columns = [
        'occurred',
        'type_code',
        'user',
        'note',
    ]

    form_fields = [
        'person',
        'product',
        'product_brand',
        'product_description',
        'product_size',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'unit_price',
        'total_price',
        'paid_amount',
        'status_code',
    ]

    def query(self, session):
        return session.query(model.CustomerOrderItem)\
                      .join(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrderItem.order)\
                               .joinedload(model.CustomerOrder.person))

    def configure_grid(self, g):
        super(CustomerOrderItemsView, self).configure_grid(g)

        g.set_joiner('person', lambda q: q.outerjoin(model.Person))

        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            default_active=True, default_verb='contains')

        g.set_sorter('person', model.Person.display_name)
        g.set_sorter('order_created', model.CustomerOrder.created)

        g.set_sort_defaults('order_created', 'desc')

        g.set_type('case_quantity', 'quantity')
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')
        g.set_type('total_price', 'currency')

        g.set_renderer('person', self.render_person)
        g.set_renderer('order_created', self.render_order_created)

        g.set_label('person', "Person Name")
        g.set_label('product_brand', "Brand")
        g.set_label('product_description', "Description")
        g.set_label('product_size', "Size")
        g.set_label('status_code', "Status")

    def render_person(self, item, column):
        return item.order.person

    def render_order_created(self, item, column):
        value = localtime(self.rattail_config, item.order.created, from_utc=True)
        return raw_datetime(self.rattail_config, value)

    def configure_form(self, f):
        super(CustomerOrderItemsView, self).configure_form(f)

        # order
        f.set_renderer('order', self.render_order)

        # product
        f.set_renderer('product', self.render_product)

        # product uom
        f.set_enum('product_unit_of_measure', self.enum.UNIT_OF_MEASURE)

        # quantity fields
        f.set_type('case_quantity', 'quantity')
        f.set_type('cases_ordered', 'quantity')
        f.set_type('units_ordered', 'quantity')

        # currency fields
        f.set_type('unit_price', 'currency')
        f.set_type('total_price', 'currency')
        f.set_type('paid_amount', 'currency')

        # person
        f.set_renderer('person', self.render_person)

        # label overrides
        f.set_label('status_code', "Status")

    def render_order(self, item, field):
        order = item.order
        if not order:
            return ""
        text = six.text_type(order)
        url = self.request.route_url('custorders.view', uuid=order.uuid)
        return tags.link_to(text, url)

    def get_row_data(self, item):
        return self.Session.query(model.CustomerOrderItemEvent)\
                           .filter(model.CustomerOrderItemEvent.item == item)\
                           .order_by(model.CustomerOrderItemEvent.occurred,
                                     model.CustomerOrderItemEvent.type_code)

    def configure_row_grid(self, g):
        super(CustomerOrderItemsView, self).configure_row_grid(g)
        g.set_label('occurred', "When")
        g.set_label('type_code', "What") # TODO: enum renderer
        g.set_label('user', "Who")
        g.set_label('note', "Notes")


def includeme(config):
    CustomerOrderItemsView.defaults(config)

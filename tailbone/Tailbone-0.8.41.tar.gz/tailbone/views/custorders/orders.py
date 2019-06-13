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
Customer Order Views
"""

from __future__ import unicode_literals, absolute_import

import six
from sqlalchemy import orm

from rattail.db import model

from webhelpers2.html import tags

from tailbone.db import Session
from tailbone.views import MasterView


class CustomerOrdersView(MasterView):
    """
    Master view for customer orders
    """
    model_class = model.CustomerOrder
    route_prefix = 'custorders'
    creatable = False
    editable = False
    deletable = False

    grid_columns = [
        'id',
        'customer',
        'person',
        'created',
        'status_code',
    ]

    form_fields = [
        'id',
        'customer',
        'person',
        'created',
        'status_code',
    ]

    def query(self, session):
        return session.query(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrder.customer))

    def configure_grid(self, g):
        super(CustomerOrdersView, self).configure_grid(g)

        g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
        g.set_joiner('person', lambda q: q.outerjoin(model.Person))

        g.filters['customer'] = g.make_filter('customer', model.Customer.name,
                                              label="Customer Name",
                                              default_active=True,
                                              default_verb='contains')
        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            label="Person Name",
                                            default_active=True,
                                            default_verb='contains')

        g.set_sorter('customer', model.Customer.name)
        g.set_sorter('person', model.Person.display_name)

        g.set_sort_defaults('created', 'desc')

        # TODO: enum choices renderer
        g.set_label('status_code', "Status")
        g.set_label('id', "ID")

    def configure_form(self, f):
        super(CustomerOrdersView, self).configure_form(f)

        # id
        f.set_readonly('id')
        f.set_label('id', "ID")

        # person
        f.set_renderer('person', self.render_person)

        # created
        f.set_readonly('created')

        # label overrides
        f.set_label('status_code', "Status")

    def render_person(self, order, field):
        person = order.person
        if not person:
            return ""
        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)


def includeme(config):
    CustomerOrdersView.defaults(config)

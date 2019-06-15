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
Member Views
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa

from rattail.db import model

from deform import widget as dfwidget

from tailbone import grids
from tailbone.views import MasterView


class MemberView(MasterView):
    """
    Master view for the Member class.
    """
    model_class = model.Member
    is_contact = True
    has_versions = True

    labels = {
        'id': "ID",
    }

    grid_columns = [
        'id',
        'person',
        'customer',
        'email',
        'phone',
        'active',
        'equity_current',
        'joined',
        'withdrew',
    ]

    form_fields = [
        'id',
        'person',
        'customer',
        'default_email',
        'default_phone',
        'active',
        'equity_current',
        'equity_payment_due',
        'joined',
        'withdrew',
    ]

    def configure_grid(self, g):
        super(MemberView, self).configure_grid(g)

        g.set_joiner('person', lambda q: q.outerjoin(model.Person))
        g.set_sorter('person', model.Person.display_name)
        g.set_filter('person', model.Person.display_name)

        g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
        g.set_sorter('customer', model.Customer.name)
        g.set_filter('customer', model.Customer.name)

        g.filters['active'].default_active = True
        g.filters['active'].default_verb = 'is_true'

        # phone
        g.set_joiner('phone', lambda q: q.outerjoin(model.MemberPhoneNumber, sa.and_(
            model.MemberPhoneNumber.parent_uuid == model.Member.uuid,
            model.MemberPhoneNumber.preference == 1)))
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.MemberPhoneNumber.number, d)())
        g.set_filter('phone', model.MemberPhoneNumber.number,
                     factory=grids.filters.AlchemyPhoneNumberFilter)
        g.set_label('phone', "Phone Number")

        # email
        g.set_joiner('email', lambda q: q.outerjoin(model.MemberEmailAddress, sa.and_(
            model.MemberEmailAddress.parent_uuid == model.Member.uuid,
            model.MemberEmailAddress.preference == 1)))
        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.MemberEmailAddress.address, d)())
        g.set_filter('email', model.MemberEmailAddress.address)
        g.set_label('email', "Email Address")

        g.set_sort_defaults('id')

        g.set_link('person')
        g.set_link('customer')

    def grid_extra_class(self, member, i):
        if not member.active:
            return 'warning'
        if not member.equity_current:
            return 'notice'

    def configure_form(self, f):
        super(MemberView, self).configure_form(f)
        member = f.model_instance

        # date fields
        f.set_type('joined', 'date_jquery')
        f.set_type('equity_payment_due', 'date_jquery')
        f.set_type('equity_last_paid', 'date_jquery')
        f.set_type('withdrew', 'date_jquery')

        # person
        if self.creating or self.editing:
            if 'person' in f.fields:
                f.replace('person', 'person_uuid')
                people = self.Session.query(model.Person)\
                                     .order_by(model.Person.display_name)
                values = [(p.uuid, six.text_type(p))
                          for p in people]
                require = False
                if not require:
                    values.insert(0, ('', "(none)"))
                f.set_widget('person_uuid', dfwidget.SelectWidget(values=values))
                f.set_label('person_uuid', "Person")
        else:
            f.set_readonly('person')
            # f.set_renderer('person', self.render_person)

        # customer
        if self.creating or self.editing:
            if 'customer' in f.fields:
                f.replace('customer', 'customer_uuid')
                customers = self.Session.query(model.Customer)\
                                          .order_by(model.Customer.name)
                values = [(c.uuid, six.text_type(c))
                          for c in customers]
                require = False
                if not require:
                    values.insert(0, ('', "(none)"))
                f.set_widget('customer_uuid', dfwidget.SelectWidget(values=values))
                f.set_label('customer_uuid', "Customer")
        else:
            f.set_readonly('customer')
            # f.set_renderer('customer', self.render_customer)

        # default_email
        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and member.emails:
            f.set_default('default_email', member.emails[0].address)

        # default_phone
        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and member.phones:
            f.set_default('default_phone', member.phones[0].number)

        if self.creating:
            f.remove_fields(
                'equity_total',
                'equity_last_paid',
                'equity_payment_credit',
                'withdrew',
            )

    def render_default_email(self, member, field):
        if member.emails:
            return member.emails[0].address

    def render_default_phone(self, member, field):
        if member.phones:
            return member.phones[0].number


def includeme(config):
    MemberView.defaults(config)

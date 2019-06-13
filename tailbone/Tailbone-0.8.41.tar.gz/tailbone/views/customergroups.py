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
CustomerGroup Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.db import Session
from tailbone.views import MasterView


class CustomerGroupsView(MasterView):
    """
    Master view for the CustomerGroup class.
    """
    model_class = model.CustomerGroup
    model_title = "Customer Group"

    labels = {
        'id': "ID",
    }

    grid_columns = [
        'id',
        'name',
    ]

    form_fields = [
        'id',
        'name',
    ]

    def configure_grid(self, g):
        super(CustomerGroupsView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')
        g.set_link('id')
        g.set_link('name')

    def before_delete(self, group):
        # First remove customer associations.
        q = Session.query(model.CustomerGroupAssignment)\
            .filter(model.CustomerGroupAssignment.group == group)
        for assignment in q:
            Session.delete(assignment)

    @classmethod
    def defaults(cls, config):

        # fix permission group title
        config.add_tailbone_permission_group('customergroups', "Customer Groups")

        cls._defaults(config)


def includeme(config):
    CustomerGroupsView.defaults(config)

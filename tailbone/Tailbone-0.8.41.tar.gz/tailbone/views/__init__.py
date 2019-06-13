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
Pyramid Views
"""

from __future__ import unicode_literals, absolute_import

from .core import View
from .master import MasterView

# TODO: deprecate / remove some of this
from .autocomplete import AutocompleteView


def includeme(config):

    # core views
    config.include('tailbone.views.common')
    config.include('tailbone.views.auth')

    # main table views
    config.include('tailbone.views.bouncer')
    config.include('tailbone.views.brands')
    config.include('tailbone.views.categories')
    config.include('tailbone.views.customergroups')
    config.include('tailbone.views.customers')
    config.include('tailbone.views.datasync')
    config.include('tailbone.views.departments')
    config.include('tailbone.views.depositlinks')
    config.include('tailbone.views.email')
    config.include('tailbone.views.employees')
    config.include('tailbone.views.families')
    config.include('tailbone.views.handheld')
    config.include('tailbone.views.inventory')
    config.include('tailbone.views.labels')
    config.include('tailbone.views.messages')
    config.include('tailbone.views.people')
    config.include('tailbone.views.products')
    config.include('tailbone.views.progress')
    config.include('tailbone.views.purchases')
    config.include('tailbone.views.reportcodes')
    config.include('tailbone.views.reports')
    config.include('tailbone.views.roles')
    config.include('tailbone.views.settings')
    config.include('tailbone.views.shifts')
    config.include('tailbone.views.stores')
    config.include('tailbone.views.subdepartments')
    config.include('tailbone.views.taxes')
    config.include('tailbone.views.upgrades')
    config.include('tailbone.views.users')
    config.include('tailbone.views.vendors')

    # batch views
    config.include('tailbone.views.batch.newproduct')
    config.include('tailbone.views.batch.pricing')
    config.include('tailbone.views.batch.product')

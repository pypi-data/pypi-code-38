# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Mobile Grids
"""

from __future__ import unicode_literals, absolute_import

from pyramid.renderers import render

from .core import Grid


class MobileGrid(Grid):
    """
    Base class for all mobile grids
    """

    def render_filters(self, template='/mobile/grids/filters_simple.mako', **kwargs):
        context = kwargs
        context['request'] = self.request
        context['grid'] = self
        return render(template, context)

    def render_grid(self, template='/mobile/grids/grid.mako', **kwargs):
        context = kwargs
        context['grid'] = self
        return render(template, context)

    def render_complete(self, template='/mobile/grids/complete.mako', **kwargs):
        context = kwargs
        context['grid'] = self
        return render(template, context)

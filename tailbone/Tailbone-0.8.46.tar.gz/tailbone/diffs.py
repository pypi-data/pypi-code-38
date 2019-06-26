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
Tools for displaying data diffs
"""

from __future__ import unicode_literals, absolute_import

from pyramid.renderers import render
from webhelpers2.html import HTML


class Diff(object):
    """
    Core diff class.  In sore need of documentation.
    """

    def __init__(self, old_data, new_data, columns=None, fields=None, render_field=None, render_value=None, monospace=False,
                 extra_row_attrs=None):
        self.old_data = old_data
        self.new_data = new_data
        self.columns = columns or ["field name", "old value", "new value"]
        self.fields = fields or self.make_fields()
        self._render_field = render_field or self.render_field_default
        self.render_value = render_value or self.render_value_default
        self.monospace = monospace
        self.extra_row_attrs = extra_row_attrs

    def make_fields(self):
        return sorted(set(self.old_data) | set(self.new_data), key=lambda x: x.lower())

    def old_value(self, field):
        return self.old_data.get(field)

    def new_value(self, field):
        return self.new_data.get(field)

    def values_differ(self, field):
        return self.new_value(field) != self.old_value(field)

    def render_html(self, template='/diff.mako', **kwargs):
        context = kwargs
        context['diff'] = self
        return HTML.literal(render(template, context))

    def get_row_attrs(self, field):
        """
        Returns a *rendered* set of extra attributes for the ``<tr>`` element
        for the given field.  May be an empty string, or a snippet of HTML
        attribute syntax, e.g.:

        .. code-highlight:: none

           class="diff" foo="bar"

        If you wish to supply additional attributes, please define
        :attr:`extra_row_attrs`, which can be either a static dict, or a
        callable returning a dict.
        """
        attrs = {}
        if self.values_differ(field):
            attrs['class'] = 'diff'

        if self.extra_row_attrs:
            if callable(self.extra_row_attrs):
                attrs.update(self.extra_row_attrs(field, attrs))
            else:
                attrs.update(self.extra_row_attrs)

        return HTML.render_attrs(attrs)

    def render_field(self, field):
        return self._render_field(field, self)

    def render_field_default(self, field, diff):
        return field

    def render_value_default(self, field, value):
        return repr(value)

    def render_old_value(self, field):
        value = self.old_value(field)
        return self.render_value(field, value)

    def render_new_value(self, field):
        value = self.new_value(field)
        return self.render_value(field, value)

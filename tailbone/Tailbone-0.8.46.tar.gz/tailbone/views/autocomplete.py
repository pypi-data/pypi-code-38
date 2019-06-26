# -*- coding: utf-8 -*-
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
Autocomplete View
"""

from __future__ import unicode_literals, absolute_import

from tailbone.views.core import View
from tailbone.db import Session


class AutocompleteView(View):
    """
    Base class for generic autocomplete views.
    """

    def prepare_term(self, term):
        """
        If necessary, massage the incoming search term for use with the query.
        """
        return term

    def filter_query(self, q):
        return q

    def make_query(self, term):
        q = Session.query(self.mapped_class)
        q = self.filter_query(q)
        q = q.filter(getattr(self.mapped_class, self.fieldname).ilike('%%%s%%' % term))
        q = q.order_by(getattr(self.mapped_class, self.fieldname))
        return q

    def query(self, term):
        return self.make_query(term)

    def display(self, instance):
        return getattr(instance, self.fieldname)

    def value(self, instance):
        """
        Determine the data value for a query result instance.
        """
        return instance.uuid

    def get_data(self, term):
        return self.query(term).all()

    def __call__(self):
        """
        View implementation.
        """
        term = self.request.params.get(u'term') or u''
        term = term.strip()
        if term:
            term = self.prepare_term(term)
        if not term:
            return []
        results = self.get_data(term)
        return [{'label': self.display(x), 'value': self.value(x)} for x in results]

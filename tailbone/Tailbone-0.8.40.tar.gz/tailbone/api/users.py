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
Tailbone Web API - User Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from cornice.resource import resource, view

from tailbone.api import APIMasterView


@resource(collection_path='/users', path='/users/{uuid}')
class UserView(APIMasterView):

    model_class = model.User

    def normalize(self, user):
        return {
            'uuid': user.uuid,
            'username': user.username,
            'person_display_name': (user.person.display_name or '') if user.person else '',
            'active': user.active,
        }

    def interpret_sortcol(self, order_by):
        if order_by == 'person_display_name':
            return self.sortcol('Person', 'display_name')
        return self.sortcol(order_by)

    def join_for_sort_model(self, query, model_name):
        if model_name == 'Person':
            query = query.outerjoin(model.Person)
        return query

    @view(permission='users.list')
    def collection_get(self):
        return self._collection_get()

    @view(permission='users.view')
    def get(self):
        return self._get()


def includeme(config):
    config.scan(__name__)

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
Tailbone Web API - Master View
"""

from __future__ import unicode_literals, absolute_import

from rattail.config import parse_bool

from tailbone.api import APIView, api
from tailbone.db import Session


class SortColumn(object):

    def __init__(self, field_name, model_name=None):
        self.field_name = field_name
        self.model_name = model_name


class APIMasterView(APIView):
    """
    Base class for data model REST API views.
    """

    @property
    def Session(self):
        return Session

    @classmethod
    def get_model_class(cls):
        if hasattr(cls, 'model_class'):
            return cls.model_class
        raise NotImplementedError("must set `model_class` for {}".format(cls.__name__))

    @classmethod
    def get_normalized_model_name(cls):
        if hasattr(cls, 'normalized_model_name'):
            return cls.normalized_model_name
        return cls.get_model_class().__name__.lower()

    @classmethod
    def get_object_key(cls):
        if hasattr(cls, 'object_key'):
            return cls.object_key
        return cls.get_normalized_model_name()

    @classmethod
    def get_collection_key(cls):
        if hasattr(cls, 'collection_key'):
            return cls.collection_key
        return '{}s'.format(cls.get_object_key())

    def make_sort_spec(self):

        # these params are based on 'vuetable-2'
        # https://www.vuetable.com/guide/sorting.html#initial-sorting-order
        if 'sort' in self.request.params:
            sort = self.request.params['sort']
            sortkey, sortdir = sort.split('|')
            if sortdir != 'desc':
                sortdir = 'asc'
            return [
                {
                    # 'model': self.model_class.__name__,
                    'field': sortkey,
                    'direction': sortdir,
                },
            ]

        # these params are based on 'vue-tables-2'
        # https://github.com/matfish2/vue-tables-2#server-side
        if 'orderBy' in self.request.params and 'ascending' in self.request.params:
            sortcol = self.interpret_sortcol(self.request.params['orderBy'])
            if sortcol:
                spec = {
                    'field': sortcol.field_name,
                    'direction': 'asc' if parse_bool(self.request.params['ascending']) else 'desc',
                }
                if sortcol.model_name:
                    spec['model'] = sortcol.model_name
                return [spec]

    def interpret_sortcol(self, order_by):
        """
        This must return a ``SortColumn`` object based on parsing of the given
        ``order_by`` string, which is "raw" as received from the client.

        Please override as necessary, but in all cases you should invoke
        :meth:`sortcol()` to obtain your return value.  Default behavior
        for this method is to simply do (only) that::

           return self.sortcol(order_by)

        Note that you can also return ``None`` here, if the given ``order_by``
        string does not represent a valid sort.
        """
        return self.sortcol(order_by)

    def sortcol(self, *args):
        """
        Return a simple ``SortColumn`` object which denotes the field and
        optionally, the model, to be used when sorting.
        """
        if len(args) == 1:
            return SortColumn(args[0])
        elif len(args) == 2:
            return SortColumn(args[1], args[0])
        else:
            raise ValueError("must pass 1 arg (field_name) or 2 args (model_name, field_name)")

    def join_for_sort_spec(self, query, sort_spec):
        """
        This should apply any joins needed on the given query, to accommodate
        requested sorting as per ``sort_spec`` - which will be non-empty but
        otherwise no claims are made regarding its contents.

        Please override as necessary, but in all cases you should return a
        query, either untouched or else with join(s) applied.
        """
        model_name = sort_spec[0].get('model')
        return self.join_for_sort_model(query, model_name)

    def join_for_sort_model(self, query, model_name):
        """
        This should apply any joins needed on the given query, to accommodate
        requested sorting on a field associated with the given model.

        Please override as necessary, but in all cases you should return a
        query, either untouched or else with join(s) applied.
        """
        return query

    def make_pagination_spec(self):

        # these params are based on 'vuetable-2'
        # https://github.com/ratiw/vuetable-2-tutorial/wiki/prerequisite#sample-api-endpoint
        if 'page' in self.request.params and 'per_page' in self.request.params:
            page = self.request.params['page']
            per_page = self.request.params['per_page']
            if page.isdigit() and per_page.isdigit():
                return int(page), int(per_page)

        # these params are based on 'vue-tables-2'
        # https://github.com/matfish2/vue-tables-2#server-side
        if 'page' in self.request.params and 'limit' in self.request.params:
            page = self.request.params['page']
            limit = self.request.params['limit']
            if page.isdigit() and limit.isdigit():
                return int(page), int(limit)

    def _collection_get(self):
        from sqlalchemy_filters import apply_sort, apply_pagination

        cls = self.get_model_class()
        query = self.Session.query(cls)
        context = {}

        # maybe sort query
        sort_spec = self.make_sort_spec()
        if sort_spec:
            query = self.join_for_sort_spec(query, sort_spec)
            query = apply_sort(query, sort_spec)

            # maybe paginate query
            pagination_spec = self.make_pagination_spec()
            if pagination_spec:
                number, size = pagination_spec
                query, pagination = apply_pagination(query, page_number=number, page_size=size)

                # these properties are based on 'vuetable-2'
                # https://www.vuetable.com/guide/pagination.html#how-the-pagination-component-works
                context['total'] = pagination.total_results
                context['per_page'] = pagination.page_size
                context['current_page'] = pagination.page_number
                context['last_page'] = pagination.num_pages
                context['from'] = pagination.page_size * (pagination.page_number - 1) + 1
                to = pagination.page_size * (pagination.page_number - 1) + pagination.page_size
                if to > pagination.total_results:
                    context['to'] = pagination.total_results
                else:
                    context['to'] = to

                # these properties are based on 'vue-tables-2'
                # https://github.com/matfish2/vue-tables-2#server-side
                context['count'] = pagination.total_results

        objects = [self.normalize(obj) for obj in query]

        # TODO: test this for ratbob!
        context[self.get_collection_key()] = objects

        # these properties are based on 'vue-tables-2'
        # https://github.com/matfish2/vue-tables-2#server-side
        context['data'] = objects
        if 'count' not in context:
            context['count'] = len(objects)

        return context

    def _get(self):
        uuid = self.request.matchdict['uuid']
        obj = self.Session.query(self.get_model_class()).get(uuid)
        if not obj:
            raise self.notfound()
        return {self.get_object_key(): self.normalize(obj)}

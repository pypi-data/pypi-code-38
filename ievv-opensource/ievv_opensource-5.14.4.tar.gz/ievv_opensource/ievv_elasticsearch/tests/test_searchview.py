from django.test import TestCase, RequestFactory
from django.views.generic import View
from django_cradmin.datetimeutils import default_timezone_datetime

from ievv_opensource.ievv_elasticsearch import search
from ievv_opensource.ievv_elasticsearch.viewhelpers import searchview


class TestViewMixin(TestCase):
    def setUp(self):
        self.searchapi = search.Connection.get_instance()
        self.searchapi.clear_all_data()

    def test_first_page(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'User A'},
            id=1)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'User B'},
            id=2)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'User C'},
            id=3)

        class MySearchView(View, searchview.ViewMixin):
            page_size = 2

            def get_search_query(self):
                return {
                    'match_all': {}
                }

            def get_search_sort(self):
                return {'name': {'order': 'asc'}}

        request = RequestFactory().get('/test')
        view = MySearchView()
        view.request = request
        paginator = view.get_paginator()
        self.assertEquals(paginator.number_of_items_in_current_page, 2)
        resultitems = list(paginator)
        self.assertEquals(resultitems[0].source['name'], 'User A')
        self.assertEquals(resultitems[1].source['name'], 'User B')
        self.assertTrue(paginator.has_next())
        self.assertFalse(paginator.has_previous())

    def test_last_page(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'User A'},
            id=1)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'User B'},
            id=2)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'User C'},
            id=3)

        class MySearchView(View, searchview.ViewMixin):
            page_size = 2

            def get_search_query(self):
                return {
                    'match_all': {}
                }

            def get_search_sort(self):
                return {'name': {'order': 'asc'}}

        request = RequestFactory().get('/test?p=1')
        view = MySearchView()
        view.request = request
        paginator = view.get_paginator()
        self.assertEquals(paginator.number_of_items_in_current_page, 1)
        resultitems = list(paginator)
        self.assertEquals(resultitems[0].source['name'], 'User C')
        self.assertFalse(paginator.has_next())
        self.assertTrue(paginator.has_previous())


class TestSortMixin(TestCase):
    def setUp(self):
        self.searchapi = search.Connection.get_instance()
        self.searchapi.clear_all_data()

    def test_sort_default(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser A', 'created_datetime': default_timezone_datetime(2014, 1, 1)},
            id=1)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser B', 'created_datetime': default_timezone_datetime(2015, 1, 1)},
            id=2)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser C', 'created_datetime': default_timezone_datetime(2015, 1, 1)},
            id=3)

        class MySearchView(searchview.SortMixin, searchview.View):
            default_sort_keyword = 'name'

            sort_map = {
                'name': {'name': {'order': 'asc'}},
                'created': {'created_datetime': {'order': 'desc'}},
            }

            def get_search_query(self):
                return {
                    'match_all': {}
                }

        request = RequestFactory().get('/test')
        view = MySearchView()
        view.request = request
        paginator = view.get_paginator()
        resultitems = list(paginator)
        self.assertEquals(resultitems[0].id, '1')
        self.assertEquals(resultitems[1].id, '2')
        self.assertEquals(resultitems[2].id, '3')

    def test_default_specified(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser A', 'created_datetime': default_timezone_datetime(2014, 1, 1)},
            id=1)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser B', 'created_datetime': default_timezone_datetime(2015, 1, 1)},
            id=2)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser C', 'created_datetime': default_timezone_datetime(2015, 1, 1)},
            id=3)

        class MySearchView(searchview.SortMixin, searchview.View):
            default_sort_keyword = 'name'

            sort_map = {
                'name': {'name': {'order': 'asc'}},
                'created': {'created_datetime': {'order': 'desc'}},
            }

            def get_search_query(self):
                return {
                    'match_all': {}
                }

        request = RequestFactory().get('/test?o=name')
        view = MySearchView()
        view.request = request
        paginator = view.get_paginator()
        resultitems = list(paginator)
        self.assertEquals(resultitems[0].id, '1')
        self.assertEquals(resultitems[1].id, '2')
        self.assertEquals(resultitems[2].id, '3')

    def test_alternative(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser A', 'created_datetime': default_timezone_datetime(2014, 1, 1)},
            id=1)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser B', 'created_datetime': default_timezone_datetime(2015, 1, 1)},
            id=2)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser C', 'created_datetime': default_timezone_datetime(2013, 1, 1)},
            id=3)

        class MySearchView(searchview.SortMixin, searchview.View):
            default_sort_keyword = 'name'

            sort_map = {
                'name': {'name': {'order': 'asc'}},
                'created': {'created_datetime': {'order': 'desc'}},
            }

            def get_search_query(self):
                return {
                    'match_all': {}
                }

        request = RequestFactory().get('/test?o=created')
        view = MySearchView()
        view.request = request
        paginator = view.get_paginator()
        resultitems = list(paginator)
        self.assertEquals(resultitems[0].id, '2')
        self.assertEquals(resultitems[1].id, '1')
        self.assertEquals(resultitems[2].id, '3')


class TestSearchMixin(TestCase):
    def setUp(self):
        self.searchapi = search.Connection.get_instance()
        self.searchapi.clear_all_data()

    def test_search(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser A'},
            id=1)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser B'},
            id=2)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Somethingelse'},
            id=3)

        class MySearchView(searchview.SearchMixin, searchview.View):
            search_query_fields = ['name']

        request = RequestFactory().get('/test?s=Testuser')
        view = MySearchView()
        view.request = request
        paginator = view.get_paginator()
        resultitems = list(paginator)
        ids = set([resultitem.id for resultitem in resultitems])
        self.assertEquals(ids, {'1', '2'})

    def test_no_search_string(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser A'},
            id=1)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser B'},
            id=2)
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Somethingelse'},
            id=3)

        class MySearchView(searchview.SearchMixin, searchview.View):
            search_query_fields = ['name']

        request = RequestFactory().get('/test')
        view = MySearchView()
        view.request = request
        paginator = view.get_paginator()
        resultitems = list(paginator)
        ids = set([resultitem.id for resultitem in resultitems])
        self.assertEquals(ids, {'1', '2', '3'})

from django.test import TestCase
from django_cradmin.datetimeutils import default_timezone_datetime
from pyelasticsearch import ElasticHttpNotFoundError

from ievv_opensource.ievv_elasticsearch import search


class TestConnectionClearAllData(TestCase):
    def setUp(self):
        self.searchapi = search.Connection.get_instance()

    def test_clear_all_removes_indexes_and_data(self):
        self.searchapi.index(
            index='testone',
            doc_type='testitem',
            doc={'name': 'Test One'},
            id=1)
        self.searchapi.index(
            index='testtwo',
            doc_type='testitem',
            doc={'name': 'Test Two'},
            id=1)

        # No errors from these before we clear all
        self.searchapi.elasticsearch.get('testone', 'testitem', 1)
        self.searchapi.elasticsearch.get('testtwo', 'testitem', 1)

        self.searchapi.clear_all_data()
        with self.assertRaises(ElasticHttpNotFoundError):
            self.searchapi.elasticsearch.get('testone', 'testitem', 1)
        with self.assertRaises(ElasticHttpNotFoundError):
            self.searchapi.elasticsearch.get('testtwo', 'testitem', 1)


class TestConnection(TestCase):
    def setUp(self):
        self.searchapi = search.Connection.get_instance()
        self.searchapi.clear_all_data()

    def test_add_data_get(self):
        added_person = self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Joe Tester', 'age': 25, 'title': 'QA Master'},
            id=1)
        self.assertEqual(added_person['_type'], 'person')
        self.assertEqual(added_person['_index'], 'contacts')
        self.assertEqual(added_person['_id'], '1')
        self.assertEqual(added_person['_version'], 1)
        self.assertTrue(added_person['created'])

        fetched_person = self.searchapi.elasticsearch.get('contacts', 'person', 1)
        self.assertEqual(fetched_person['_type'], 'person')
        self.assertEqual(fetched_person['_index'], 'contacts')
        self.assertEqual(fetched_person['_id'], '1')
        self.assertEqual(fetched_person['_version'], 1)
        self.assertEqual(fetched_person['_source'], {
            'name': 'Joe Tester', 'age': 25, 'title': 'QA Master'})

    def test_index_datetime(self):
        self.searchapi.index(
            index='testitems',
            doc_type='testitem',
            doc={'created_datetime': default_timezone_datetime(2015, 1, 1)},
            id=1)
        fetched = self.searchapi.elasticsearch.get('testitems', 'testitem', 1)
        self.assertEqual(fetched['_source']['created_datetime'], '2015-01-01T00:00:00+00:00')

    def test_search(self):
        self.searchapi.bulk_index(
            index='contacts',
            doc_type='person',
            docs=[{'name': 'Joe Tester'},
                  {'name': 'Peter The Super Tester'}])

        multiresult = self.searchapi.search({
            'query': {
                'match': {
                    'name': {
                        'query': 'Tester'
                    }
                }
            }
        })
        singleresult = self.searchapi.search({
            'query': {
                'match': {
                    'name': {
                        'query': 'Joe'
                    }
                }
            }
        })
        self.assertEqual(multiresult['hits']['total'], 2)
        self.assertEqual(multiresult['hits']['hits'][0]['_source']['name'], 'Joe Tester')
        self.assertEqual(multiresult['hits']['hits'][1]['_source']['name'], 'Peter The Super Tester')
        self.assertEqual(singleresult['hits']['total'], 1)
        self.assertEqual(singleresult['hits']['hits'][0]['_source']['name'], 'Joe Tester')

    def test_search_match_all(self):
        self.searchapi.bulk_index(
            index='contacts',
            doc_type='person',
            docs=[{'name': 'Joe Tester'},
                  {'name': 'Peter The Super Tester'}])
        result = self.searchapi.search({
            'query': {
                'match_all': {}
            }
        })
        self.assertEqual(result['hits']['total'], 2)

    def test_wrapped_search(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Joe Tester'})

        result = self.searchapi.wrapped_search({
            'query': {
                'match_all': {}
            }
        })
        self.assertEqual(result.total, 1)
        resultitem = list(result)[0]
        self.assertEqual(resultitem.index, 'contacts')
        self.assertEqual(resultitem.doc_type, 'person')
        self.assertEqual(resultitem.source, {'name': 'Joe Tester'})


class TestPaginator(TestCase):
    def setUp(self):
        self.searchapi = search.Connection.get_instance()
        self.searchapi.clear_all_data()

    def test_sanity(self):
        self.searchapi.index(
            index='contacts',
            doc_type='person',
            doc={'name': 'Testuser'},
            id=1)
        paginator = self.searchapi.paginated_search({
            'query': {
                'match_all': {}
            }
        })
        self.assertEquals(len(list(paginator)), 1)

    def test_multiple_pages_first_page(self):
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
        paginator = self.searchapi.paginated_search({
            'query': {
                'match_all': {}
            },
            'sort': {'name': {'order': 'asc'}}
        }, page_number=0, page_size=1)
        self.assertEquals(list(paginator)[0].source['name'], 'User A')
        self.assertTrue(paginator.has_next())
        self.assertFalse(paginator.has_previous())

    def test_multiple_pages_middle_page(self):
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
        paginator = self.searchapi.paginated_search({
            'query': {
                'match_all': {}
            },
            'sort': {'name': {'order': 'asc'}}
        }, page_number=1, page_size=1)
        self.assertEquals(list(paginator)[0].source['name'], 'User B')
        self.assertTrue(paginator.has_next())
        self.assertTrue(paginator.has_previous())

    def test_multiple_pages_last_page(self):
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
        paginator = self.searchapi.paginated_search({
            'query': {
                'match_all': {}
            },
            'sort': {'name': {'order': 'asc'}}
        }, page_number=2, page_size=1)
        self.assertEquals(list(paginator)[0].source['name'], 'User C')
        self.assertFalse(paginator.has_next())
        self.assertTrue(paginator.has_previous())

import elasticsearch_dsl
from django import test
from elasticsearch_dsl.connections import connections

from ievv_opensource import ievv_elasticsearch2


class PersonSearch(ievv_elasticsearch2.Search):
    def query_name(self, name):
        return self.query('match', name=name)


class FancyPersonSearch(ievv_elasticsearch2.Search):
    def query_all(self, text):
        return self.query(ievv_elasticsearch2.Q('match', name=text) | ievv_elasticsearch2.Q('match', description=text))


class PersonDocType(ievv_elasticsearch2.DocType):
    objects = PersonSearch()
    fancysearch = FancyPersonSearch()

    name = elasticsearch_dsl.String()
    description = elasticsearch_dsl.String()

    class Meta:
        index = 'main'


class TestSearch(test.TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        self.es.indices.delete(index='_all')
        self.es.indices.flush(index='_all')

    def test_use_search_without_doctype(self):
        self.es.index(index='test', doc_type='person', id=1, body={
            'name': 'Peter'
        })
        self.es.indices.flush()
        result = ievv_elasticsearch2.Search()\
            .query('match', name='Peter')\
            .execute()
        self.assertEqual(1, len(result))
        self.assertEqual('Peter', result[0].name)

    def test_use_search_without_doctype_match_all(self):
        self.es.index(index='test', doc_type='person', id=1, body={
            'name': 'John Doe',
            'description': 'The man'
        })
        self.es.index(index='test', doc_type='person', id=2, body={
            'name': 'Jane Doe',
            'description': 'The woman'
        })
        self.es.index(index='test', doc_type='person', id=3, body={
            'name': 'Jack Doe',
            'description': 'Unknown'
        })
        self.es.indices.flush()
        result = ievv_elasticsearch2.Search()\
            .query('multi_match', query='The', fields=['_all'])\
            .sort('name')\
            .execute()
        self.assertEqual(2, len(result))
        self.assertEqual('Jane Doe', result[0].name)
        self.assertEqual('John Doe', result[1].name)

    def test_use_doctype(self):
        PersonDocType.ievvinitialize_and_create_in_index()
        person = PersonDocType(name='Peter',
                               description='The Pan')
        person.save(flush=True)
        result = PersonDocType.objects.query_name(name='Peter').execute()
        self.assertEqual(1, len(result))
        self.assertEqual('Peter', result[0].name)

    def test_extra_search_object(self):
        PersonDocType.ievvinitialize_and_create_in_index()
        person = PersonDocType(name='Peter',
                               description='The Pan')
        person.save(flush=True)
        result = PersonDocType.fancysearch.query_all(text='Pan').execute()
        self.assertEqual(1, len(result))
        self.assertEqual('Peter', result[0].name)

    def test_underlying_elasticsearchdsl_doctype(self):
        PersonDocType.ievvinitialize_and_create_in_index()
        person = PersonDocType(name='Peter',
                               description='The Pan')
        person.save(flush=True)
        result = PersonDocType.elasticsearch_dsl_doctype_class.search()\
            .query('match', name='Peter').execute()
        self.assertEqual(1, len(result))
        self.assertEqual('Peter', result[0].name)

    def test_get_error(self):
        PersonDocType.init()
        person = PersonDocType(name='Peter',
                               description='The Pan')
        person.save(flush=True)
        with self.assertRaises(ievv_elasticsearch2.exceptions.NotFoundError):
            PersonDocType.get(id=10)

    # def test_debug(self):
    #     PersonDocType.ievvinitialize()
    #     PersonDocType.init()
    #     person = PersonDocType(name='Peter',
    #                            description='The Pan')
    #     person.save(flush=True)
    #     self.es.indices.flush()
    #
    #     search = ievv_elasticsearch2.Search()\
    #         .query('match', name='Peter')
    #     result = search.execute()
    #     pprint(result)
    #
    #     search = ievv_elasticsearch2.Search()\
    #         .query('multi_match', query='The', fields=['_all'])
    #     result = search.execute()
    #     pprint(result)
    #
    #     search = PersonDocType.objects.query_name(name='Peter')
    #     result = search.execute()
    #     pprint(result)
    #
    #     search = PersonDocType.fancysearch.query_all(text='Pan')
    #     result = search.execute()
    #     pprint(result)
    #
    #     search = PersonDocType.elasticsearch_dsl_doctype_class.search().query('match', name='Peter')
    #     result = search.execute()
    #     pprint(result)
    #
    #     for match in ievv_elasticsearch2.Search().query('match_all').execute():
    #         print(match.to_dict())

from django.test import TestCase

from ievv_opensource.ievv_elasticsearch import search, autoindex


class TestAbstractIndex(TestCase):
    def setUp(self):
        self.searchapi = search.Connection.get_instance()
        self.searchapi.clear_all_data()

    def test_index_items(self):
        class MyIndex(autoindex.AbstractIndex):
            name = 'items'

        class ProductIndexDocument(autoindex.AbstractDictDocument):
            doc_type = 'product'

        index = MyIndex()
        index.index_items([
            ProductIndexDocument({'name': 'Product One'}, id=1),
            ProductIndexDocument({'name': 'Product Two'}, id=2),
        ])
        self.searchapi.refresh()
        self.searchapi.get(index=MyIndex.name, doc_type=ProductIndexDocument.doc_type, id=1)
        self.searchapi.get(index=MyIndex.name, doc_type=ProductIndexDocument.doc_type, id=2)
        self.assertEquals(self.searchapi.wrapped_search_all().total, 2)

    def test_index_items_multiple_document_types(self):
        class MyIndex(autoindex.AbstractIndex):
            name = 'items'

        class ProductIndexDocument(autoindex.AbstractDictDocument):
            doc_type = 'product'

        class NewsIndexDocument(autoindex.AbstractDictDocument):
            doc_type = 'news'

        index = MyIndex()
        index.index_items([
            ProductIndexDocument({'name': 'Product'}, id=1),
            NewsIndexDocument({'name': 'Newsitem'}, id=1),
        ])
        self.searchapi.refresh()
        self.searchapi.get(index=MyIndex.name, doc_type=ProductIndexDocument.doc_type, id=1)
        self.searchapi.get(index=MyIndex.name, doc_type=NewsIndexDocument.doc_type, id=1)
        self.assertEquals(self.searchapi.wrapped_search_all().total, 2)

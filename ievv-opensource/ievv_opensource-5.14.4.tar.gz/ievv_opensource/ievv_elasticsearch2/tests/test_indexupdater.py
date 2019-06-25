import unittest
from unittest import mock

import elasticsearch_dsl
from django import test
from elasticsearch_dsl.connections import connections
from model_mommy import mommy

from ievv_opensource import ievv_elasticsearch2
from ievv_opensource.ievv_elasticsearch2.tests.ievv_elasticsearch2_testapp.models import ModelmapperModel


class PersonDocType(ievv_elasticsearch2.DocType):
    indexupdater = ievv_elasticsearch2.IndexUpdater()
    name = elasticsearch_dsl.String()

    class Meta:
        index = 'main'


@unittest.skip('Not ready')
class TestIndexUpdaterBulkIndex(test.TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        self.es.indices.delete(index='_all')
        self.es.indices.flush(index='_all')
        PersonDocType.ievvinitialize_and_create_in_index()

    def test_single(self):
        person = PersonDocType(name='Test')
        person.meta.id = 1
        PersonDocType.indexupdater.bulk_index([person])
        person = person.get_from_index()
        self.assertEqual('Test', person.name)

    def test_multiple(self):
        person1 = PersonDocType(name='Test1')
        person1.meta.id = 10
        person2 = PersonDocType(name='Test2')
        person2.meta.id = 20
        person3 = PersonDocType(name='Test3')
        person3.meta.id = 30
        PersonDocType.indexupdater.bulk_index([person1, person2, person3])

        person1 = person1.get_from_index()
        person2 = person2.get_from_index()
        person3 = person3.get_from_index()
        self.assertEqual('Test1', person1.name)
        self.assertEqual('Test2', person2.name)
        self.assertEqual('Test3', person3.name)


class AutomappedDocType(ievv_elasticsearch2.ModelDocType):
    model_class = ModelmapperModel

    class Meta:
        index = 'main'


@unittest.skip('Not ready')
class TestIndexUpdatedBulkIndexModelIds(test.TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        self.es.indices.delete(index='_all')
        self.es.indices.flush(index='_all')
        AutomappedDocType.ievvinitialize_and_create_in_index()

    def test_single(self):
        item = mommy.make(ModelmapperModel, char='a')
        AutomappedDocType.indexupdater.bulk_index_model_ids(ids=[item.id])
        self.assertEqual('a', AutomappedDocType.get(id=item.id).char)

    def test_multiple(self):
        item1 = mommy.make(ModelmapperModel, char='a')
        item2 = mommy.make(ModelmapperModel, char='b')
        item3 = mommy.make(ModelmapperModel, char='c')
        AutomappedDocType.indexupdater.bulk_index_model_ids(ids=[item1.id, item2.id, item3.id])
        self.assertEqual('a', AutomappedDocType.get(id=item1.id).char)
        self.assertEqual('b', AutomappedDocType.get(id=item2.id).char)
        self.assertEqual('c', AutomappedDocType.get(id=item3.id).char)


@unittest.skip('Not ready')
class TestIndexUpdaterBulkReindexByPriority(test.TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        self.es.indices.delete(index='_all')
        self.es.indices.flush(index='_all')

    def test_iterate_doctype_objects_for_reindexing_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            ievv_elasticsearch2.IndexUpdater().bulk_reindex_by_priority()

    def test_iterate_doctype_objects_for_reindexing_implemented(self):
        mockobject = mock.MagicMock()

        class MyIndexUpdater(ievv_elasticsearch2.IndexUpdater):
            def iterate_doctype_objects_for_reindexing(self, priority=None, using=None):
                mockobject()

            def bulk_index(self, doctype_object_iterable, using=None):
                pass

        MyIndexUpdater().bulk_reindex_by_priority()
        mockobject.assert_called_once_with()

    def test_iterate_doctype_objects_for_reindexing_priority_and_using_forwarded(self):
        mockobject = mock.MagicMock()

        class MyIndexUpdater(ievv_elasticsearch2.IndexUpdater):
            def iterate_doctype_objects_for_reindexing(self, priority=None, using=None):
                mockobject(priority=priority, using=using)

            def bulk_index(self, doctype_object_iterable, using=None):
                pass

        MyIndexUpdater().bulk_reindex_by_priority(priority=MyIndexUpdater.PRIORITY_HIGH,
                                                  using='otherserver')
        mockobject.assert_called_once_with(priority=MyIndexUpdater.PRIORITY_HIGH,
                                           using='otherserver')

    def test_bulk_reindex_by_priority_no_model_objects_to_index(self):
        AutomappedDocType().indexupdater.bulk_reindex_by_priority()

    def test_bulk_reindex_by_priority(self):
        AutomappedDocType.init()
        item1 = mommy.make(ModelmapperModel, char='a')
        item2 = mommy.make(ModelmapperModel, char='b')
        item3 = mommy.make(ModelmapperModel, char='c')
        AutomappedDocType().indexupdater.bulk_reindex_by_priority()
        self.assertEqual('a', AutomappedDocType.get(id=item1.id).char)
        self.assertEqual('b', AutomappedDocType.get(id=item2.id).char)
        self.assertEqual('c', AutomappedDocType.get(id=item3.id).char)

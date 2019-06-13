from DateTime import DateTime
from ftw.topics.interfaces import IBackReferenceCollector
from ftw.topics.testing import EXAMPLE_CONTENT_DEFAULT_FUNCTIONAL
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface.verify import verifyObject


class TestDefaultCollector(TestCase):

    layer = EXAMPLE_CONTENT_DEFAULT_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.subsite = self.portal.get('foo').get('subsite')
        self.subsite_uid = IUUID(self.subsite)
        self.empty_subsite = self.portal.get('empty-subsite')
        self.empty_subsite_uid = IUUID(self.empty_subsite)

        self.tree = self.portal.get('topics')
        self.node = self.tree.get('manufacturing')
        self.subsite_tree = self.subsite.get('topics')
        self.subsite_node = self.subsite_tree.get('manufacturing')

        self.doc = self.portal.get('manufacturing-processes')
        self.subsite_doc = self.subsite.get('theories')

    def test_component_registered(self):
        self.assertTrue(
            queryMultiAdapter((self.node, None), IBackReferenceCollector),
            'No default IBackReferenceCollector adapter registered.')

    def test_component_implements_interface(self):
        comp = getMultiAdapter((self.node, None), IBackReferenceCollector)
        self.assertTrue(IBackReferenceCollector.providedBy(comp))
        verifyObject(IBackReferenceCollector, comp)

    def test_calling_returns_result(self):
        comp = getMultiAdapter((self.node, None),
                               IBackReferenceCollector)
        result = comp()

        self.assertEquals(
            [
                {'label': u'Plone site',
                 'UID': 'root',
                 'path': '/plone',
                 'objects': [self.doc],
                 'is_current_section': True},

                {'label': 'Sub Site',
                 'UID': self.subsite_uid,
                 'path': '/plone/foo/subsite',
                 'objects': [self.subsite_doc]}],
            result)

    def test_SUBSITE_calling_returns_result(self):
        comp = getMultiAdapter((self.subsite_node, None),
                               IBackReferenceCollector)
        result = comp()

        self.assertEquals(
            [
                {'label': u'Plone site',
                 'UID': 'root',
                 'path': '/plone',
                 'objects': [self.doc]},

                {'label': 'Sub Site',
                 'UID': self.subsite_uid,
                 'path': '/plone/foo/subsite',
                 'objects': [self.subsite_doc],
                 'is_current_section': True}],
            result)

    def test_get_sections(self):
        comp = getMultiAdapter((self.node, None), IBackReferenceCollector)
        self.assertEquals(
            [
                {'label': u'Plone site',
                 'UID': 'root',
                 'path': '/plone',
                 'objects': [],
                 'is_current_section': True},

                {'label': 'Sub Site',
                 'UID': self.subsite_uid,
                 'objects': [],
                 'path': '/plone/foo/subsite'},

                {'label': "Empty sub site",
                 'UID': self.empty_subsite_uid,
                 'objects': [],
                 'path': '/plone/empty-subsite'}],
            comp.get_sections())

    def test_get_brefs_per_section(self):
        comp = getMultiAdapter((self.node, None),
                               IBackReferenceCollector)
        result = comp._get_brefs_per_section()

        self.assertEquals(
            [
                {'label': u'Plone site',
                 'UID': 'root',
                 'path': '/plone',
                 'objects': [self.doc],
                 'is_current_section': True},

                {'label': 'Sub Site',
                 'UID': self.subsite_uid,
                 'path': '/plone/foo/subsite',
                 'objects': [self.subsite_doc]}],
            result)

    def test_SUBSITE_get_brefs_per_section(self):
        comp = getMultiAdapter((self.subsite_node, None),
                               IBackReferenceCollector)
        result = comp._get_brefs_per_section()

        self.assertEquals(
            [
                {'label': u'Plone site',
                 'UID': 'root',
                 'path': '/plone',
                 'objects': [self.doc]},

                {'label': 'Sub Site',
                 'UID': self.subsite_uid,
                 'path': '/plone/foo/subsite',
                 'objects': [self.subsite_doc],
                 'is_current_section': True}],
            result)

    def test_get_merged_brefs(self):
        comp = getMultiAdapter((self.node, None),
                               IBackReferenceCollector)

        result = comp._get_merged_brefs()
        self.assertIn(self.doc, result)
        self.assertIn(self.subsite_doc, result)

    def test_SUBSITE_get_merged_brefs(self):
        comp = getMultiAdapter((self.subsite_node, None),
                               IBackReferenceCollector)

        result = comp._get_merged_brefs()
        self.assertIn(self.doc, result)
        self.assertIn(self.subsite_doc, result)

    def test_get_similar_topic_objects(self):
        comp = getMultiAdapter((self.node, None),
                               IBackReferenceCollector)

        result = comp._get_similar_topic_objects()
        self.assertIn(self.node, result)
        self.assertIn(self.subsite_node, result)

    def test_SUBSITE_get_similar_topic_objects(self):
        comp = getMultiAdapter((self.subsite_node, None),
                               IBackReferenceCollector)

        result = comp._get_similar_topic_objects()
        self.assertIn(self.node, result)
        self.assertIn(self.subsite_node, result)

    def test_exclude_expired_content(self):
        comp = getMultiAdapter((self.node, None),
                               IBackReferenceCollector)

        self.assertIn(self.doc, comp._get_merged_brefs())

        self.doc.setExpirationDate(DateTime() - 10)
        self.doc.reindexObject()

        self.assertNotIn(self.doc, comp._get_merged_brefs())

    def test_exclude_future_content(self):
        comp = getMultiAdapter((self.node, None),
                               IBackReferenceCollector)

        self.assertIn(self.doc, comp._get_merged_brefs())

        self.doc.setEffectiveDate(DateTime() + 10)
        self.doc.reindexObject()

        self.assertNotIn(self.doc, comp._get_merged_brefs())

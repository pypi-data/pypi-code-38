from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.topics.interfaces import ITopicSupport
from ftw.topics.testing import SIMPLELAYOUT_TOPICS_FUNCTIONAL_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


class TestSchemaExtender(TestCase):

    layer = SIMPLELAYOUT_TOPICS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_extends_ITopicSupport(self):
        page = self.portal.get(self.portal.invokeFactory(
                               'ContentPage', 'page'))

        self.assertTrue(
            ITopicSupport.providedBy(page),
            'Expected ContentPage objects to provide ITopicSupport'
            ' but it doesnt.')

        field = page.Schema().get('topics')
        self.assertTrue(field, 'Field "topics" missing on ContentPage')

    def test_does_not_extend_others(self):
        obj = self.portal.get(self.portal.invokeFactory('File', 'file'))

        self.assertFalse(ITopicSupport.providedBy(obj),
                         'Did not expect "File" to provide "ITopicSupport"')

        field = obj.Schema().get('topics')
        self.assertFalse(
            field, '"File" object should not have "topics" field')

    @browsing
    def test_extends_ITopicSupport_with_versioning(self, browser):
        portal_repository = getToolByName(self.portal, 'portal_repository')
        portal_repository.setVersionableContentTypes(['File', ])

        file_ = create(Builder('file')
                       .with_dummy_content()
                       .providing(ITopicSupport))

        browser.login().visit(file_, view='edit')
        self.assertTrue(len(browser.css('#archetypes-fieldname-topics')),
                        'Field "topics" missing on File')

        browser.fill({'cmfeditions_save_new_version': True}).save()

        self.assertTrue(browser.url.startswith(file_.absolute_url()))

        browser.visit(file_, view='@@historyview')
        self.assertEquals(1,
                          len(browser.css('.historyRecord')),
                          'Expect one history entry')

from ftw.topics.interfaces import ITopic
from ftw.topics.interfaces import ITopicTree
from ftw.topics.testing import TOPICS_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from unittest2 import TestCase
import transaction


class TestContentTypeCreation(TestCase):

    layer = TOPICS_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        transaction.commit()

        self.browser = Browser(self.layer['app'])
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME, TEST_USER_PASSWORD,))
        self.browser.handleErrors = False

    def test_create_topic_tree(self):
        self.browser.open(self.portal.portal_url())
        self.browser.getLink(id='ftw-topics-topictree').click()

        self.assertTrue(
            self.browser.url.endswith('++add++ftw.topics.TopicTree'),
            'Should be on the topic tree add view, but url is: %s' % (
                self.browser.url))

        self.browser.getControl(label='Title').value = 'Topical'
        self.browser.getControl(label='Save').click()

        self.assertTrue(
            self.browser.url.endswith('topical/view'),
            'Should be on "topical" view, but url is: %s' % (
                self.browser.url))
        self.assertIn('Topical', self.browser.contents)

        tree = self.portal.get('topical')
        self.assertTrue(ITopicTree.providedBy(tree))

    def test_create_topic(self):
        # first create a tree
        self.browser.open('http://nohost/plone/++add++ftw.topics.TopicTree')
        self.browser.getControl(label='Title').value = 'Topical'
        self.browser.getControl(label='Save').click()

        self.assertEqual(self.browser.url,
                         'http://nohost/plone/topical/view')

        factory_link = self.browser.getLink(id='ftw-topics-topic')
        self.assertTrue(
            factory_link,
            'There is no "Topic" factory link on the topic tree view.')
        factory_link.click()

        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/topical/++add++ftw.topics.Topic')
        self.browser.getControl(label='Title').value = 'Manufacturing'
        self.browser.getControl(label='Save').click()

        self.assertEqual(self.browser.url,
                         'http://nohost/plone/topical/manufacturing/view')
        self.assertIn('Manufacturing', self.browser.contents)

        topic = self.portal.get('topical').get('manufacturing')
        self.assertTrue(ITopic.providedBy(topic))

from Products.Five.browser import BrowserView
from ftw.topics.interfaces import ITopicBrowserLayer
from ftw.topics.testing import SIMPLELAYOUT_TOPICS_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager


class TestReferencesViewletOnPage(TestCase):

    layer = SIMPLELAYOUT_TOPICS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.page = self.portal.get(
            self.portal.invokeFactory('ContentPage', 'page'))

    def test_registered(self):
        # Only Registered for ITopicSupport
        self.assertFalse(self.viewlet(self.portal))
        self.assertTrue(self.viewlet(self.page))

    def test_not_available_without_references(self):
        self.assertFalse(self.viewlet().available())

    def test_available_with_references(self):
        topic1, topic2 = self.create_topic_tree("A topic", "B topic")

        self.reference_topics(topic1, topic2)
        self.assertTrue(self.viewlet().available())

        result = [
            dict(title='A topic',
                 description='',
                 url=topic1.absolute_url()),
            dict(title='B topic',
                 description='',
                 url=topic2.absolute_url()), ]

        self.assertEquals(result, self.viewlet().get_references())

    def test_references_without_view_permissions_are_not_visible(self):
        about_peter, = self.create_topic_tree("About Peter")

        self.reference_topics(about_peter)
        self.assert_references(['About Peter'])

        about_peter.manage_permission('View', roles=[], acquire=False)
        self.assert_references([])
        self.assertFalse(self.viewlet().available(),
                         "Viewlet without visible references should not be available")

    def create_topic_tree(self, *topic_titles):
        tree = self.portal.get(
            self.portal.invokeFactory('ftw.topics.TopicTree', 'tree'))

        for i, topic_title in enumerate(topic_titles):
            tree.invokeFactory('ftw.topics.Topic', 'topic%i' % i,
                               title=topic_title)
        return tree.objectValues()

    def viewlet(self, context=None):
        if context is None:
            context = self.page
        alsoProvides(context.REQUEST, ITopicBrowserLayer)

        view = BrowserView(context, context.REQUEST)
        manager_name = 'plone.belowcontent'
        manager = queryMultiAdapter(
            (context, context.REQUEST, view),
            IViewletManager,
            manager_name)
        self.failUnless(manager)

        # Set up viewlets
        manager.update()
        name = 'ftw.topics.references'
        viewlets = [v for v in manager.viewlets if v.__name__ == name]
        if len(viewlets) == 0:
            return None
        else:
            self.assertEquals(1, len(viewlets),
                              "There should only be one viewlet!")
            return viewlets[0]

    def reference_topics(self, *topics):
        self.page.Schema()['topics'].set(
            self.page, [t.UID() for t in topics])

    def assert_references(self, references):
        reference_titles = [v['title'] for v in self.viewlet().get_references()]
        self.assertEquals(references, reference_titles)

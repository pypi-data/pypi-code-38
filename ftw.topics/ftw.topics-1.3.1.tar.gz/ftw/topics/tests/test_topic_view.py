from ftw.testbrowser import browsing
from ftw.topics.testing import EXAMPLE_CONTENT_DEFAULT_FUNCTIONAL
from ftw.topics.testing import EXAMPLE_CONTENT_SIMPLELAYOUT_FUNCTIONAL
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.browserlayer.layer import mark_layer
from plone.mocktestcase.dummy import Dummy
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from pyquery import PyQuery
from unittest2 import TestCase
from zope.component import getMultiAdapter
import transaction


def links_to_text(pq_resultset):
    return map(lambda node: node.text.strip(), pq_resultset)


class TestDefaultTopicView(TestCase):

    layer = EXAMPLE_CONTENT_DEFAULT_FUNCTIONAL
    viewname = 'topic_view'

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.subsite = self.portal.get('foo').get('subsite')

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.tree = self.portal.get('topics')
        self.node = self.tree.get('manufacturing')
        self.subnode = self.node.get('agile-manufacturing')
        self.topic_technology = self.tree.get('technology')

        self.subsite_tree = self.subsite.get('topics')
        self.subsite_node = self.subsite_tree.get('manufacturing')

        self.browser = Browser(self.layer['app'])
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD,))
        self.browser.handleErrors = False

        mark_layer(None, Dummy(request=self.request))

    def test_default_topic_view(self):
        portal_types = getToolByName(self.portal, 'portal_types')
        fti = portal_types.get('ftw.topics.Topic')
        self.assertEqual(
            fti.default_view, self.viewname,
            'Expected default view to be %s on "ftw.topics.Topic"'
            ' since only the default GS profile was installed' % (
                self.viewname))

    def test_subnode_listed(self):
        self.browser.open(self.node.absolute_url() + '/' + self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertEqual(doc('h2.subelements-heading').text(), 'Topics',
                         'Expected a "Topics" heading')

        # on node (Manufacturing) should be subnode (Agile Manufacturing)
        links = doc('.subelements-listing a')
        self.assertEqual(len(links), 2,
                         'Found more or less links than expected')

        self.assertEqual(links.text(), 'Agile Manufacturing Quality')

    def test_subnode_has_no_children(self):
        self.browser.open(self.subnode.absolute_url() + '/' + self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertFalse(doc('h2.subelements-heading'),
                         'Expected no "Topics" heading')

    def test_default_section_filter_selection(self):
        self.browser.open(self.node.absolute_url() + '/' + self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertEquals(doc('.topic-filter li b').text().strip(),
                          'Plone site',
                          'Expected section "Plone site" to be ' +
                          'selected by default.')

        filter_links = links_to_text(doc('.topic-filter li a'))
        self.assertIn('Sub Site', filter_links,
                      'Missing awailable section filter "Sub Site"')

        reference_links = links_to_text(doc('.topic-reference-listings a'))
        self.assertIn(
            'Manufacturing processes', reference_links,
            'Link "Manufacturing processes" should be shown')

        self.assertNotIn(
            'Theories', reference_links,
            'Link "Theories" should not be shown, it is in'
            ' the section "Sub Site", not "Plone site"')

    def test_other_section_filter(self):
        self.browser.open(self.node.absolute_url() + '/' + self.viewname)
        self.browser.getLink('Sub Site').click()
        doc = PyQuery(self.browser.contents)

        self.assertEquals(doc('.topic-filter li b').text().strip(),
                          'Sub Site',
                          'Expected section "Sub Site" to be ' +
                          'selected by default.')

        filter_links = links_to_text(doc('.topic-filter li a'))
        self.assertIn('Plone site', filter_links,
                      'Missing awailable section filter "Plone site"')

        reference_links = links_to_text(doc('.topic-reference-listings a'))
        self.assertNotIn(
            'Manufacturing processes', reference_links,
            'Link "Manufacturing processes" should not be shown, it is in'
            ' the section "Sub Site", not "Plone site"')

        self.assertIn(
            'Theories', reference_links,
            'Link "Theories" should be shown')

    def test_SUBSITE_default_section_filter_selection(self):
        self.browser.open(self.subsite_node.absolute_url() + '/' +
                          self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertEquals(doc('.topic-filter li b').text().strip(),
                          'Sub Site',
                          'Expected section "Sub Site" to be ' +
                          'selected by default.')

        filter_links = links_to_text(doc('.topic-filter li a'))
        self.assertIn('Plone site', filter_links,
                      'Missing awailable section filter "Plone site"')

        reference_links = links_to_text(doc('.topic-reference-listings a'))
        self.assertNotIn(
            'Manufacturing processes', reference_links,
            'Link "Manufacturing processes" should not be shown, it is in'
            ' the section "Sub Site", not "Plone site"')

        self.assertIn(
            'Theories', reference_links,
            'Link "Theories" should be shown')

    def test_sections_are_always_shown_when_there_are_subsites_and_brefs(self):
        self.browser.open(self.topic_technology.absolute_url() + '/' +
                          self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertEquals(
            doc('.topic-filter li').text(), 'Plone site',
            'Only Plone site should be shown as section, because there'
            ' are other sections (subsites) - even when there is only one'
            ' section shown.')

    def test_sections_are_not_shown_when_there_are_subsites_but_no_brefs(self):
        self.topic_quality = self.node.get('quality')
        self.browser.open(self.topic_quality.absolute_url() + '/' +
                          self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertEquals(doc('.topic-filter li'), [],
                          'Expect no section, because there is no content')

    def test_sections_are_shown_when_other_sections_have_brefs(self):
        obj = self.subsite_tree.get('technology')
        self.browser.open(obj.absolute_url() + '/' + self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertEquals(
            ['Plone site', 'Sub Site'],
            map(lambda node: PyQuery(node).text(), doc('.topic-filter li')),
            'Section filter should be visible because other sections have'
            ' backreferences.')

    def test_no_section_are_shown_when_there_are_no_subsites(self):
        # delete all "subsites", so that we have only one "section",
        # which is the site.
        self.portal.manage_delObjects(['foo', 'empty-subsite'])
        transaction.commit()

        self.browser.open(self.topic_technology.absolute_url() + '/' +
                          self.viewname)
        doc = PyQuery(self.browser.contents)

        self.assertEquals(
            0, len(doc('.topic-filter')),
            'Sections should not be shown in a non-subsite setup.')

    def test_backreferences_without_view_permissions_are_not_visible(self):
        folder = self.portal.get('foo')
        folder.Schema()['topics'].set(folder, self.subnode.UID())

        self.topicview = getMultiAdapter((self.subnode, self.request),
                                         name='topic_view')

        self.assert_references(['Foo'])

        folder.manage_permission('View', roles=[], acquire=False)

        self.assert_references([])

    def assert_references(self, references):
        self.topicview()
        reference_titles = [v['title'] for v in self.topicview.objects]
        self.assertEquals(references, reference_titles)

    @browsing
    def test_settings_can_hide_backreferences(self, browser):
        browser.login(username=SITE_OWNER_NAME, password=SITE_OWNER_PASSWORD)

        browser.visit(self.topic_technology)
        self.assertTrue(browser.css('.referenceRepresentationListing'))

        browser.visit(self.topic_technology, view='edit')
        browser.fill({'Show backreferences': False}).submit()

        self.assertFalse(browser.css('.referenceRepresentationListing'))


class TestSimplelayoutTopicView(TestDefaultTopicView):

    layer = EXAMPLE_CONTENT_SIMPLELAYOUT_FUNCTIONAL
    viewname = 'simplelayout'

    def setUp(self):
        super(TestSimplelayoutTopicView, self).setUp()

        self.page = self.portal.get(self.portal.invokeFactory(
            'ContentPage', 'page', title="Page 1"))

        self.folder = self.portal.get(
            self.portal.invokeFactory('Folder', 'folder', title="Folder"))
        transaction.commit()

    def test_representation_contentpage(self):
        self.page.Schema()['topics'].set(self.page, IUUID(self.subnode))
        self.page.reindexObject()
        transaction.commit()

        self.browser.open(self.subnode.absolute_url())
        doc = PyQuery(self.browser.contents)

        self.assertEquals(
            len(doc('.referenceRepresentationListing ul li a')), 1,
            'Found more or less links than expected')

        self.assertEquals(
            len(doc('.referenceRepresentationTitle')), 1,
            'Found more or less links than expected')

    def test_representation_default(self):
        self.folder.Schema()['topics'].set(self.folder, IUUID(self.subnode))
        self.folder.reindexObject()
        transaction.commit()

        self.browser.open(self.subnode.absolute_url())
        doc = PyQuery(self.browser.contents)

        self.assertEquals(
            len(doc('.referenceRepresentationListing ul li a')), 1,
            'Found more or less links than expected')

        self.assertEquals(
            len(doc('.referenceRepresentationTitle')), 1,
            'Found more or less links than expected')

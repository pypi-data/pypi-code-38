from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from ftw.testing import MockTestCase
from ftw.topics.finder import DefaultTopicTreeFinder
from ftw.topics.interfaces import ITopicRootFinder
from ftw.topics.interfaces import ITopicTree
from ftw.topics.testing import ZCML_LAYER
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.component import queryMultiAdapter
from zope.component.hooks import setSite
from zope.interface.verify import verifyClass


class TestDefaultTopicTreeFinder(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):
        super(TestDefaultTopicTreeFinder, self).setUp()
        self.request = self.stub_request()

    def tearDown(self):
        super(TestDefaultTopicTreeFinder, self).tearDown()
        setSite(None)

    def create_tree(self, with_trees=True):
        objs = {}

        objs['site'] = self.providing_stub(IPloneSiteRoot, INavigationRoot)
        self.expect(objs['site'].getPhysicalPath()).result(['', 'site'])
        self.expect(objs['site'].getSiteManager).result(getSiteManager)

        if with_trees:
            objs['root'] = self.providing_stub(ITopicRootFinder)
            self.expect(objs['site'].objectValues()).result([
                    objs['root']])
        else:
            self.expect(objs['site'].objectValues()).result([])

        objs['foo'] = self.stub()
        self.expect(objs['foo'].getPhysicalPath()).result(['', 'site', 'foo'])
        self.set_parent(objs['foo'], objs['site'])

        objs['subsite'] = self.providing_stub(INavigationRoot)
        self.expect(objs['subsite'].getPhysicalPath()).result(
            ['', 'site', 'subsite'])
        self.set_parent(objs['subsite'], objs['site'])

        objs['bar'] = self.stub()
        self.expect(objs['bar'].getPhysicalPath()).result(
            ['', 'site', 'subsite', 'bar'])
        self.set_parent(objs['bar'], objs['subsite'])

        if with_trees:
            objs['subtree'] = self.providing_stub(ITopicTree)
            self.expect(objs['subsite'].objectValues()).result([
                    objs['subtree']])
        else:
            self.expect(objs['subsite'].objectValues()).result([])

        return objs

    def test_adapter_implements_interface(self):
        self.replay()
        self.assertTrue(
            ITopicRootFinder.implementedBy(DefaultTopicTreeFinder))
        verifyClass(ITopicRootFinder, DefaultTopicTreeFinder)

    def test_adapter_registered(self):
        context = self.create_dummy()
        self.replay()

        self.assertTrue(
            queryMultiAdapter((context, self.request), ITopicRootFinder),
            'ZugTopicTreeFinder adapter is not registered')

    def test_finds_next_navigation_root(self):
        objs = self.create_tree(with_trees=True)
        self.replay()

        obj = objs['foo']
        finder = getMultiAdapter((obj, self.request), ITopicRootFinder)

        self.assertEqual(finder.get_topic_root_path(), '/site')

    def test_subsite_obj_finds_subsite_with_trees(self):
        objs = self.create_tree(with_trees=True)
        self.replay()

        obj = objs['bar']
        finder = getMultiAdapter((obj, self.request), ITopicRootFinder)

        self.assertEqual(finder.get_topic_root_path(), '/site/subsite')

    def test_subsite_obj_finds_site_without_trees(self):
        objs = self.create_tree(with_trees=False)
        self.replay()

        obj = objs['bar']
        finder = getMultiAdapter((obj, self.request), ITopicRootFinder)

        self.assertEqual(finder.get_topic_root_path(), '/site')

    def test_finds_site_on_site(self):
        objs = self.create_tree(with_trees=True)
        self.replay()

        obj = objs['site']
        finder = getMultiAdapter((obj, self.request), ITopicRootFinder)

        self.assertEqual(finder.get_topic_root_path(), '/site')

    def test_fall_back_to_plone_site_root(self):
        site = self.create_dummy(getSiteManager=getSiteManager,
                                 getPhysicalPath=lambda: ('', 'site'))
        setSite(site)
        self.replay()

        finder = getMultiAdapter((self.create_dummy(), self.request),
                                 ITopicRootFinder)

        self.assertEqual(finder.get_topic_root_path(), '/site')

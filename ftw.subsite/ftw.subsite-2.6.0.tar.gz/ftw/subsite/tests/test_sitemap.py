from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.browser.sitemap import SubsiteSitemapQueryBuilder
from ftw.subsite.testing import FTW_SUBSITE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestSubsiteSitemap(TestCase):

    layer = FTW_SUBSITE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.subsite = create(Builder('subsite').titled(u'My Subsite'))
        self.folder = create(Builder('folder')
                             .titled(u'Folder')
                             .within(self.subsite))

    def test_subsite_query_builder_on_plone_root(self):
        query = SubsiteSitemapQueryBuilder(self.portal)()

        self.assertEquals(query['path']['query'], '/plone',
                          'Expect portal root')

    def test_subsite_query_builder_on_subsite(self):
        query = SubsiteSitemapQueryBuilder(self.subsite)()

        self.assertEquals(query['path']['query'], '/plone/my-subsite',
                          'Expect subsite path')

    def test_subsite_query_builder_on_folder_in_subsite(self):
        query = SubsiteSitemapQueryBuilder(self.folder)()

        self.assertEquals(
            query['path']['query'], '/plone/my-subsite',
            'Expect subsite path, because the folder is in a subsite')

    @browsing
    def test_subsite_sitemap_view_on_plone_root(self, browser):
        browser.login().visit(self.portal, view='sitemap')
        self.assertEquals(['My Subsite', 'Folder'],
                          browser.css('#portal-sitemap a').text)

    @browsing
    def test_subsite_sitemap_view_on_subsite_root(self, browser):
        browser.login().visit(self.portal, view='sitemap')
        self.assertEquals(['My Subsite', 'Folder'],
                          browser.css('#portal-sitemap a').text)

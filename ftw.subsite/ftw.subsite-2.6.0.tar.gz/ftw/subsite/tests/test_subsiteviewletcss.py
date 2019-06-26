from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.testing import FTW_SUBSITE_FUNCTIONAL_TESTING
from ftw.subsite.viewlets.cssviewlet import CSSViewlet
from ftw.testbrowser import browsing
from plone.app.testing import login
from unittest2 import TestCase
from zope.publisher.browser import BrowserView


class TestSubsite(TestCase):

    layer = FTW_SUBSITE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.subsite = create(Builder('subsite')
                              .titled(u'Subsute')
                              .having(additional_css='p {color: red;}'))

        self.styles = '<style type="text/css" media="all">p {color: red;}</style>'

    @browsing
    def test_cssviewlet_in_subsite(self, browser):
        browser.login().visit(self.subsite)

        self.assertIn(self.styles,
                      browser.contents,
                      'Did not found the substes styles.')
        browser.visit(self.portal)
        self.assertNotIn(self.styles,
                         browser.contents,
                         'Found unexpeted subsite styles.')

    @browsing
    def test_cssviewlet_in_subfolder(self, browser):
        folder = create(Builder('folder').within(self.subsite))
        browser.login().visit(folder)
        self.assertIn(self.styles,
                      browser.contents,
                      'Did not found the substes styles.')

    def test_do_not_fail_if_nav_root_is_not_traversable(self):
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Folder', 'ftw.subsite.Subsite'),
            'simple_publication_workflow')

        subsite = create(Builder('subsite').titled(u'MySubsite'))
        subfolder = create(Builder('folder').within(subsite))
        user = create(Builder('user').with_roles('Manager', on=subfolder))

        login(self.portal, user.getId())
        viewlet = CSSViewlet(subfolder,
                             subfolder.REQUEST,
                             BrowserView(subfolder, subfolder.REQUEST))

        self.assertEquals('', viewlet.render())

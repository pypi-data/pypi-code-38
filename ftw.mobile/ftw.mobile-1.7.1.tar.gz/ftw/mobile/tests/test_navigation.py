from ftw.builder import Builder
from ftw.builder import create
from ftw.mobile.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from operator import itemgetter
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized


class TestMobileNavigation(FunctionalTestCase):

    @browsing
    def test_startup(self, browser):
        self.maxDiff = None
        self.grant('Manager')
        create(Builder('folder').titled('six').within(
            create(Builder('folder').titled('five').within(
                create(Builder('folder').titled('four').within(
                    create(Builder('folder').titled('three').within(
                        create(Builder('folder').titled('two').within(
                            create(Builder('folder').titled('one'))))))))))))

        create(Builder('folder').titled('f').within(
            create(Builder('folder').titled('e').within(
                create(Builder('folder').titled('d').within(
                    create(Builder('folder').titled('c').within(
                        create(Builder('folder').titled('b').within(
                            create(Builder('folder').titled('a'))))))))))))

        browser.open(view='mobilenav/startup')
        expected_startup_paths = [
            u'/plone/a',
            u'/plone/a/b',
            u'/plone/a/b/c',
            u'/plone/a/b/c/d',
            u'/plone/a/b/c/d/e',
            u'/plone/one',
            u'/plone/one/two',
            u'/plone/one/two/three',
            u'/plone/one/two/three/four',
            u'/plone/one/two/three/four/five',
        ]
        self.assertItemsEqual(
            expected_startup_paths,
            map(itemgetter('absolute_path'), browser.json))

        browser.open(self.portal.one.two, view='mobilenav/startup')
        self.assertItemsEqual(
            expected_startup_paths + [
                u'/plone/one/two/three/four/five/six',
            ],
            map(itemgetter('absolute_path'), browser.json))

        # The "children_loaded" property tells the JavaScript tree store
        # whether the children of a node are expected to be delivered within
        # the same JSON response.
        # This decision is made from a query point of view, thus when the container
        # has no children it may still have a "children_loaded" property.
        # The responses are expected to contain all children of a node, or none.
        self.assertEquals(
            {False: [u'/plone/a/b/c/d',
                     u'/plone/a/b/c/d/e',
                     u'/plone/one/two/three/four/five',
                     u'/plone/one/two/three/four/five/six'],
             True: [u'/plone/a',
                    u'/plone/a/b',
                    u'/plone/a/b/c',
                    u'/plone/one',
                    u'/plone/one/two',
                    u'/plone/one/two/three',
                    u'/plone/one/two/three/four']},

            {True: map(itemgetter('absolute_path'),
                       filter(lambda item: item.get('children_loaded'),
                              sorted(browser.json,
                                     key=itemgetter('absolute_path')))),
             False: map(itemgetter('absolute_path'),
                        filter(lambda item: not item.get('children_loaded'),
                               sorted(browser.json,
                                      key=itemgetter('absolute_path'))))})

    @browsing
    def test_startup_headers(self, browser):
        browser.open(view='mobilenav/startup')
        self.assertDictContainsSubset({'content-type': 'application/json',
                                       'x-theme-disabled': 'True'},
                                      browser.headers)
        self.assertNotIn('cache-control', browser.headers,
                         'No cache headers expected when request has'
                         ' no cache key GET parameter.')

        browser.open(view='mobilenav/startup', data={'cachekey': 'abc123'})
        self.assertEquals(
            'public, max-age=31536000',
            browser.headers.get('cache-control'),
            'Expected public cache control since request is anonymous.')

        browser.login().open(view='mobilenav/startup', data={'cachekey': 'abc123'})
        self.assertEquals(
            'private, max-age=31536000',
            browser.headers.get('cache-control'),
            'Expected private cache control since request is authenticated.')

    @browsing
    def test_startup_item_data(self, browser):
        self.grant('Manager')
        create(Builder('folder')
               .titled('The Folder')
               .having(description='A very nice folder'))

        browser.open(view='mobilenav/startup')
        self.assertEquals(
            [{u'absolute_path': u'/plone/the-folder',
              u'children_loaded': True,
              u'description': u'A very nice folder',
              u'externallink': False,
              u'id': u'the-folder',
              u'title': u'The Folder',
              u'url': u'http://nohost/plone/the-folder'}],
            browser.json)

    @browsing
    def test_startup_with_no_View_permission_on_parent(self, browser):
        """Regression test: the navigation should not break when the current
        user has no View permission on any parent.
        """

        self.grant('Manager')
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['Folder'], 'simple_publication_workflow')

        one = create(Builder('folder').titled('Folder One'))
        two = create(Builder('folder').titled('Folder Two').within(one))
        john = create(Builder('user').named('John', 'Doe')
                      .with_roles('Reader', on=two))

        browser.login(john).open(two, view='mobilenav/startup')

        self.assertDictEqual(
            {u'/plone/folder-one': u'Folder One',
             u'/plone/folder-one/folder-two': u'Folder Two'},

            dict(map(lambda item: (item['absolute_path'], item['title']),
                     browser.json)))

    @browsing
    def test_startup_does_not_work_on_unauthorized_content(self, browser):
        """For security it is essential that the `startup` endpoint does
        not work on a context where the current user has no `View` permission.
        This is not protected by ZCML since the `children` endpoint needs
        to be public.

        The `startup` endpoint may provide infos of unpublished content (such
        as the title). This is necessary for the navigation to work and follows
        Plone principal but it should not be possible to misuse the endpoint
        for getting those informations on _any_ content.
        """
        self.grant('Manager')
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['Folder'], 'simple_publication_workflow')
        folder = create(Builder('folder').titled('Folder'))
        john = create(Builder('user').named('John', 'Doe'))

        browser.login(john)
        with browser.expect_unauthorized():
            browser.open(folder, view='mobilenav/startup')

    @browsing
    def test_children_endpoint_fetches_two_levels(self, browser):
        self.grant('Manager')
        create(Builder('folder').titled('Five').within(
            create(Builder('folder').titled('Four').within(
                create(Builder('folder').titled('Three').within(
                    create(Builder('folder').titled('Two').within(
                        create(Builder('folder').titled('One'))))))))))

        browser.open(self.portal.one, view='mobilenav/children')
        self.assertItemsEqual(
            [
                u'/plone/one',
                u'/plone/one/two',
                u'/plone/one/two/three',
            ],
            map(itemgetter('absolute_path'), browser.json))

        browser.open(self.portal.one.two, view='mobilenav/children')
        self.assertItemsEqual(
            [
                u'/plone/one/two',
                u'/plone/one/two/three',
                u'/plone/one/two/three/four',
            ],
            map(itemgetter('absolute_path'), browser.json))

    @browsing
    def test_children_item_data(self, browser):
        self.grant('Manager')
        create(Builder('folder')
               .titled('The Folder')
               .having(description='A very nice folder'))

        browser.open(view='mobilenav/children')
        self.assertEquals(
            [{u'absolute_path': u'/plone/the-folder',
              u'description': u'A very nice folder',
              u'externallink': False,
              u'id': u'the-folder',
              u'title': u'The Folder',
              u'url': u'http://nohost/plone/the-folder'}],
            browser.json)

    @browsing
    def test_children_fetching_on_unauthorized_works(self, browser):
        """The JavaScript may fetch children now and then, sometimes even
        on objects on which the current user has no View permission.
        In order for the JavaScript to work properly, this should not fail
        with an unauthorized error but return possible children.

        This might be a situation where the unauthorized object was already
        loaded as parent and the JavaScript is trying to fetch its children,
        which may even be published / visible.
        """

        self.grant('Manager')
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(['Folder'], 'simple_publication_workflow')

        container = create(Builder('folder').titled('Container'))
        visible_child = create(Builder('folder').titled('visible child')
                               .within(container))
        create(Builder('folder').titled('invisible child').within(container))
        john = create(Builder('user').named('John', 'Doe')
                      .with_roles('Reader', on=visible_child))

        browser.login(john).open(container, view='mobilenav/children')
        self.assertItemsEqual(
            [u'/plone/container/visible-child'],
            map(itemgetter('absolute_path'), browser.json))

    @browsing
    def test_children_loaded_flag_on_prepended_items(self, browser):
        self.grant('Manager')
        create(Builder('folder').titled('1b').within(
            create(Builder('folder').titled('1a')
                                    .having(excludeFromNav=True))))
        create(Builder('folder').titled('2a'))

        browser.open(self.portal.get('1a').get('1b'), view='mobilenav/startup')

        # 1a was prepended, since it was excluded from nav.
        response = browser.json
        self.assertIn('children_loaded', response[0])

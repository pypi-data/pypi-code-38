from ftw.builder import Builder
from ftw.builder import create
from ftw.subsite.interfaces import IFtwSubsiteLayer
from ftw.subsite.testing import FTW_SUBSITE_INTEGRATION_TESTING
from ftw.testing import IS_PLONE_5
from plone.app.testing import login
from plone.registry import Record, field
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.publisher.browser import BrowserView
from zope.viewlet.interfaces import IViewletManager
import os


class TestBannerViewlet(TestCase):

    layer = FTW_SUBSITE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def _setup_bannerfolder(self, context):
        registry = getUtility(IRegistry)
        bannerfoldername = registry.get('ftw.subsite.bannerfoldername')
        return create(Builder('folder')
                      .within(context)
                      .titled(bannerfoldername))

    def _get_viewlet(self, context, view=None):
        if not view:
            view = BrowserView(context, context.REQUEST)
            context_state = context.restrictedTraverse(
                'plone_context_state')
            view.__name__ = context_state.view_template_id()

        context.REQUEST['ACTUAL_URL'] = '/'.join((context.absolute_url(),
                                                  view.__name__))
        # invalidate caches
        del IAnnotations(context.REQUEST)['plone.memoize']

        alsoProvides(context.REQUEST, IFtwSubsiteLayer)
        manager = queryMultiAdapter(
            (context, context.REQUEST, view),
            IViewletManager,
            'plone.portalheader')
        self.failUnless(manager)
        # Set up viewlets
        manager.update()
        name = 'ftw.subsite.banner'
        return [v for v in manager.viewlets if v.__name__ == name]

    def test_component_registered(self):
        self.assertTrue(len(self._get_viewlet(self.portal)) == 1)

    def test_get_banner_folder(self):
        viewlet = self._get_viewlet(self.portal)

        # Currently there's no bannerfolder
        self.assertIsNone(viewlet[0].get_banner_folder())

        # Add banner folder
        bannerfolder = self._setup_bannerfolder(self.portal)
        self.assertEquals(viewlet[0].get_banner_folder(), bannerfolder)

    def test_get_banners(self):
        viewlet = self._get_viewlet(self.portal)
        # No banner folder
        self.assertEquals(viewlet[0].get_banners(), [])
        self.assertFalse(viewlet[0].available)

        # Add banner folder
        bannerfolder = self._setup_bannerfolder(self.portal)

        # Bannerfolder is empty
        self.assertEquals(viewlet[0].get_banners(), [])
        self.assertFalse(viewlet[0].available)

        # Add images
        image1 = bannerfolder.get(bannerfolder.invokeFactory('Image',
                                                             'image1'))
        image2 = bannerfolder.get(bannerfolder.invokeFactory('Image',
                                                             'image2'))
        if IS_PLONE_5:
            image1.reindexObject()
            image2.reindexObject()
        else:
            image1.processForm()
            image2.processForm()
        viewlet = self._get_viewlet(self.portal)  # It's cached
        self.assertEquals(len(viewlet[0].get_banners()), 2)
        self.assertTrue(viewlet[0].available)

    def test_get_banner_tag(self):
        image = self.help_import_and_preprocess_image_for_AT_and_Dext()
        viewlet = self._get_viewlet(self.portal)
        self.assertIn("height", viewlet[0].get_banner_tag())
        self.assertIn("width", viewlet[0].get_banner_tag())
        self.assertIn(self.portal.title_or_id(), viewlet[0].get_banner_tag())
        self.assertIn("%s/@@images" % image.absolute_url(),
                      viewlet[0].get_banner_tag())

    def test_available_on_navroot(self):
        self.help_import_and_preprocess_image_for_AT_and_Dext()
        viewlet = self._get_viewlet(self.portal)
        # Default is only on navroot
        self.assertTrue(viewlet[0].available)

        folder = self.portal.get(self.portal.invokeFactory('Folder',
                                                           'folder'))
        # Not on sub content
        viewlet = self._get_viewlet(folder)
        self.assertFalse(viewlet[0].available)

    def test_available_everywhere(self):
        self.help_import_and_preprocess_image_for_AT_and_Dext()
        registry = getUtility(IRegistry)
        registry.records['ftw.subsite.banner_root_only'] = \
            Record(field.Bool(title=u"dummy", default=True),
                   value=False)

        viewlet = self._get_viewlet(self.portal)
        # On nav root
        self.assertTrue(viewlet[0].available)

        folder = self.portal.get(self.portal.invokeFactory('Folder',
                                                           'folder'))
        # On sub content
        viewlet = self._get_viewlet(folder)
        self.assertTrue(viewlet[0].available)

    def test_on_subsite(self):
        subsite = create(Builder('subsite').titled(u'MySubsite'))

        viewlet = self._get_viewlet(subsite)
        self.assertTrue(len(viewlet) == 1)
        image = self.help_import_and_preprocess_image_for_AT_and_Dext(subsite)

        self.assertIn("MySubsite", viewlet[0].get_banner_tag())
        self.assertIn("%s/@@images" % image.absolute_url(),
                      viewlet[0].get_banner_tag())

    def test_find_image_in_subfolder(self):
        bannerfolder = self._setup_bannerfolder(self.portal)
        subfolder = create(Builder('folder')
                           .titled(u'Subfolder')
                           .within(bannerfolder))
        create(Builder('image').within(subfolder))

        viewlet = self._get_viewlet(self.portal)
        self.assertTrue(viewlet[0].available, 'Expect to find an image')

    def test_do_not_show_on_folder_contents_when_root_only_enabled(self):
        registry = getUtility(IRegistry)
        registry.records['ftw.subsite.banner_root_only'] = \
            Record(field.Bool(title=u"dummy", default=True),
                   value=True)

        bannerfolder = self._setup_bannerfolder(self.portal)
        subfolder = bannerfolder.get(
            bannerfolder.invokeFactory('Folder', 'subfolder'))
        subfolder.invokeFactory('Image', 'image1')

        viewlet = self._get_viewlet(self.portal)
        self.assertTrue(
            viewlet[0].available,
            'Expected viewlet to be available on default view')

        folder_contents = self.portal.restrictedTraverse('folder_contents')
        viewlet = self._get_viewlet(self.portal, view=folder_contents)
        self.assertFalse(
            viewlet[0].available,
            'Expected viewlet not to be available on folder_contents,'
            ' since root_only is enabled.')

    def test_show_on_folder_contents_when_root_only_disabled(self):
        registry = getUtility(IRegistry)
        registry.records['ftw.subsite.banner_root_only'] = \
            Record(field.Bool(title=u"dummy", default=True),
                   value=False)

        bannerfolder = self._setup_bannerfolder(self.portal)
        subfolder = bannerfolder.get(
            bannerfolder.invokeFactory('Folder', 'subfolder'))
        subfolder.invokeFactory('Image', 'image1')

        viewlet = self._get_viewlet(self.portal)
        self.assertTrue(
            viewlet[0].available,
            'Expected viewlet to be available on default view')

        folder_contents = self.portal.restrictedTraverse('folder_contents')
        viewlet = self._get_viewlet(self.portal, view=folder_contents)
        self.assertTrue(
            viewlet[0].available,
            'Expected viewlet to be available on folder_contents,'
            ' since root_only is disabled.')

    def test_do_not_fail_if_nav_root_is_not_traversable(self):
        self.portal.portal_workflow.setChainForPortalTypes(
            ('Folder', 'ftw.subsite.Subsite'),
            'simple_publication_workflow')

        self._setup_bannerfolder(self.portal)
        subsite = create(Builder('subsite').titled(u'MySubsite'))
        subfolder = create(Builder('folder').within(subsite))
        user = create(Builder('user').with_roles('Manager', on=subfolder))

        login(self.portal, user.getId())
        self.assertFalse(self._get_viewlet(subfolder)[0].available)

    def help_import_and_preprocess_image_for_AT_and_Dext(self, add_withing=None):
        if not add_withing:
            add_withing = self.portal
        bannerfolder = self._setup_bannerfolder(add_withing)
        file_ = open("%s/blue.png" % os.path.split(__file__)[0], 'r')
        if IS_PLONE_5:
            from plone.namedfile.file import NamedImage
            file_ = NamedImage(data=file_, filename=u'blue.png')
            image = bannerfolder.get(
                bannerfolder.invokeFactory('Image', 'image1', image=file_))
            image.reindexObject()
        else:
            image = bannerfolder.get(
                bannerfolder.invokeFactory('Image', 'image1', image=file_))
            image.processForm()

        return image

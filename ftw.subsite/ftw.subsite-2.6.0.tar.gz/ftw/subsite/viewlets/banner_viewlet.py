from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import instance
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRoot
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from random import choice
from zExceptions import Unauthorized
from Products.CMFCore.utils import getToolByName


class Banner(common.ViewletBase):
    render = ViewPageTemplateFile('banner_viewlet.pt')

    @property
    def available(self):
        if not self.get_banners():
            return False

        registry = getUtility(IRegistry)
        root_only = registry.get('ftw.subsite.banner_root_only', True)

        if root_only:
            context_state = self.context.restrictedTraverse(
                'plone_context_state')
            return context_state.is_view_template()

        return True

    @instance.memoize
    def get_banners(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        bannerfolder = self.get_banner_folder()
        if not bannerfolder:
            return []

        registry = getUtility(IRegistry)
        root_only = registry.get('ftw.subsite.banner_root_only', True)

        query = dict(portal_type='Image',
                     path='/'.join(bannerfolder.getPhysicalPath()))
        imgs = [brain.getObject() for brain in catalog(query)]

        if root_only:
            context_state = self.context.restrictedTraverse(
                '@@plone_context_state')
            nav_root = INavigationRoot.providedBy(self.context)
            if context_state.is_portal_root() or nav_root:
                return imgs
            return []
        else:
            return imgs

    def get_banner_folder(self):
        registry = getUtility(IRegistry)

        name = registry.get('ftw.subsite.bannerfoldername', 'banners')
        bannerfolder = None
        try:
            nav_context = self.context.restrictedTraverse(
                getNavigationRoot(self.context)).aq_explicit

            bannerfolder = nav_context.restrictedTraverse(name.encode('utf-8'))
        except (KeyError, AttributeError):
            return None
        except Unauthorized:
            return None
        return bannerfolder

    def get_banner_tag(self):
        title = self.context.title_or_id()
        img = choice(self.get_banners())
        scales = img.restrictedTraverse('@@images')
        return scales.tag('image', scale='bannerimage', alt=title,
                            title=title)

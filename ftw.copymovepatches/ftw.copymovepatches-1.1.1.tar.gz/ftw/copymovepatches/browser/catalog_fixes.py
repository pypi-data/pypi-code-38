from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.ZCatalog.ProgressHandler import ZLogHandler
from ftw.copymovepatches.utils import IS_PLONE_5


if IS_PLONE_5:
    from plone.protect.utils import addTokenToUrl


class CatalogFixes(BrowserView):

    index = ViewPageTemplateFile('templates/catalog_fixes.pt')

    def __call__(self):
        return self.index()

    def rebuild_uid_index(self):
        """Rebuild uid index.
        """
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        portal_catalog._catalog.clearIndex('UID')
        portal_catalog._catalog.reindexIndex('UID', self.request,
                                             pghandler=ZLogHandler())
        IStatusMessage(self.request).addStatusMessage(
            'Rebuilt UID index.', type='info')
        return self.redirect_to_view()

    def uid_index_errors(self):
        if not hasattr(self, '_uid_index_errors'):
            portal_catalog = getToolByName(self.context, 'portal_catalog')
            uid_index = portal_catalog._catalog.indexes['UID']
            self._uid_index_errors = abs(
                len(uid_index._index) - len(uid_index._unindex))

        return self._uid_index_errors

    def rebuild_brain_metadata(self):
        """Rebuild brain metadata.
        """
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        for rid in self.get_rids_with_invalid_uid_in_metadata():
            path = portal_catalog.getpath(rid)
            obj = self.context.unrestrictedTraverse(path)
            index = portal_catalog._catalog.uids.get(path, None)
            portal_catalog._catalog.updateMetadata(obj, path, index)

        IStatusMessage(self.request).addStatusMessage(
            'Rebuild brain metadata', type='info')
        return self.redirect_to_view()

    def get_rids_with_invalid_uid_in_metadata(self):
        if self.uid_index_errors() > 0:
            # Depends on a valid uid index.
            return

        portal_catalog = getToolByName(self.context, 'portal_catalog')
        uid_index = portal_catalog._catalog.indexes['UID']

        for rid in portal_catalog._catalog.paths.keys():
            uid_from_index = uid_index._unindex.get(rid, None)
            uid_from_metadata = portal_catalog.getMetadataForRID(rid)['UID']
            if uid_from_index != uid_from_metadata:
                yield rid

    def brain_metadata_uid_errors(self):
        if self.uid_index_errors() > 0:
            # Depends on a valid uid index.
            return

        return len(tuple(self.get_rids_with_invalid_uid_in_metadata()))

    def redirect_to_view(self):
        response = self.request.RESPONSE
        target = '/'.join((self.context.portal_url(), self.__name__))
        return response.redirect(target)

    @property
    def rebuild_uid_index_url(self):
        url = self.context.portal_url() + '/copymovepatches-catalog-fixes/rebuild_uid_index'
        if IS_PLONE_5:
            return addTokenToUrl(url)
        return url

    @property
    def rebuild_brain_metadata_url(self):
        url = self.context.portal_url() + '/copymovepatches-catalog-fixes/rebuild_brain_metadata'
        if IS_PLONE_5:
            return addTokenToUrl(url)
        return url

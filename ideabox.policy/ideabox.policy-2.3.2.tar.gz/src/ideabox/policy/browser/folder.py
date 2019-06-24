# -*- coding: utf-8 -*-

from plone.app.contenttypes.browser import folder


class FolderView(folder.FolderView):
    """ Override of plone.app.contenttypes.browser.folder.FolderView """

    def results(self, **kwargs):
        """Return a content listing based result set with contents of the
        folder.

        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument

        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        results = super(FolderView, self).results(**kwargs)
        results._basesequence = [e for e in results if e.exclude_from_nav is False]
        return results

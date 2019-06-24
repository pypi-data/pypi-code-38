# -*- coding: utf-8 -*-

from Products.CMFPlone.browser.syndication.adapters import DexterityItem
from plone import api


class ProjectItem(DexterityItem):

    def __init__(self, context, feed):
        self.image = self.get_image(context)
        super(ProjectItem, self).__init__(context, feed)

    @property
    def file(self):
        if self.image:
            return self.image.image

    def get_image(self, context):
        images = context.listFolderContents(contentFilter={"portal_type": "Image"})
        if images:
            return images[0]
        else:
            portal = api.portal.get()
            if "project_default_large.jpg" in portal:
                return portal["project_default_large.jpg"]

    @property
    def file_url(self):
        url = self.base_url
        fi = self.file
        if fi is not None:
            filename = fi.filename
            if filename:
                url += '/{0}'.format(self.image.id)
        return url

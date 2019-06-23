# -*- coding: utf-8 -*-

from plone import api


class SendableAnnexes(object):
    """ """

    def __init__(self, context):
        self.context = context

    def get(self):
        pc = api.portal.get_tool('portal_catalog')
        res = []
        for brain in pc(portal_type='File', path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1}):
            res.append({'title': brain.Title, 'UID': brain.UID})
        return res

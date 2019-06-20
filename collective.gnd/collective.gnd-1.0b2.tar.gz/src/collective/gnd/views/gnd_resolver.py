# -*- coding: utf-8 -*-

from plone import api
from Products.Five.browser import BrowserView


class GndResolver(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.gnd_id = None
        travers_name_stack = self.request.get("TraversalRequestNameStack")
        if travers_name_stack:
            self.gnd_id = travers_name_stack.pop()

    def __call__(self):
        if not self.gnd_id:
            return u"could not get GND id"
        brains = api.content.find(gnd_id=self.gnd_id)
        if not brains:
            return u"Could not resolve an object for gnd_id: {0}".format(self.gnd_id)
        redirect_url = brains[0].getURL()
        return self.request.response.redirect(redirect_url, status=301)

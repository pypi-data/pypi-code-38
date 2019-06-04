# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser.view import DefaultView

from Products.Five.browser import BrowserView


class FeedItemView(DefaultView):
    """Defaul view for Feed content type."""

    def __call__(self):
        if api.user.is_anonymous():
            return self.request.response.redirect(self.context.url)
        return super(FeedItemView, self).__call__()

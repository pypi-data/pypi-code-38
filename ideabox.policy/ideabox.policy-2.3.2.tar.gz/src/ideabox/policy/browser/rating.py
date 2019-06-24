# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from cioppino.twothumbs.browser.like import LikeWidgetView
from plone import api


class ProjectRatingView(LikeWidgetView):
    index = ViewPageTemplateFile("templates/rating.pt")
    _allowed_states = ("vote",)

    @property
    def is_available(self):
        current_state = api.content.get_state(obj=self.context)
        return current_state in self._allowed_states

    def canRate(self):
        if self.is_available is False:
            return False
        return super(ProjectRatingView, self).canRate()

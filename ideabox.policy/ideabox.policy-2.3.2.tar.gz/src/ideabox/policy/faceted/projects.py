# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from ideabox.policy.utils import can_view_rating
from plone import api
from random import shuffle
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class ProjectsView(BrowserView):
    def sort_items(self, elements):
        elements = [e for e in elements]
        shuffle(elements)
        return elements

    @property
    def default_image(self):
        return "{0}/project_default.jpg".format(api.portal.get().absolute_url())

    def rating(self, context):
        return can_view_rating(context)

    def get_theme(self, key):
        if not hasattr(self, "_themes"):
            factory = getUtility(IVocabularyFactory, "collective.taxonomy.theme")
            self._themes = factory(self.context)
        try:
            return self._themes.getTerm(key).title
        except KeyError:
            return ""

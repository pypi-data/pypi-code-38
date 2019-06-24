# encoding: utf-8

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from hashlib import md5
from ideabox.policy import _
from ideabox.policy.faceted.subscriber import Randomizer
from ideabox.policy.utils import can_view_rating
from plone import api
from plone.supermodel.model import Schema
from plone.tiles import Tile
from random import shuffle
from zope import schema
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import time


class IProjectsTile(Schema):
    """A tile that displays a listing of content items"""

    title = schema.TextLine(title=_(u"Title"), required=True, default=_(u"Projects"))

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Limit projects"),
        required=False,
        default=6,
        min=1,
        max=15,
    )


class TileRandomizer(Randomizer):
    def __init__(self):
        self.key = md5(str(time.time() // 60 * 5)).hexdigest()


class BaseProjectsTile(Tile):
    template = ViewPageTemplateFile("templates/projects.pt")

    def __call__(self):
        return self.template()

    @property
    def title(self):
        return self.data.get("title") or _(u"Projects")

    def contents(self):
        limit = self.data["limit"]
        return api.content.find(
            portal_type="Project", sort_on="created", sort_order="reverse"
        )[:limit]

    def folder_projects(self):
        folder = api.content.find(portal_type="Folder", id="projets")
        if len(folder) == 1:
            return folder[0].getURL()
        return False

    def get_theme(self, key):
        if not hasattr(self, "_themes"):
            factory = getUtility(IVocabularyFactory, "collective.taxonomy.theme")
            self._themes = factory(self.context)
        try:
            return self._themes.getTerm(key).title
        except KeyError:
            return ""

    @property
    def default_image(self):
        return "{0}/project_default.jpg".format(api.portal.get().absolute_url())

    def rating(self, context):
        return can_view_rating(context)


class LatestProjectsTile(BaseProjectsTile):
    """A tile that displays a listing of content items"""

    def contents(self):
        limit = self.data["limit"]
        return api.content.find(
            portal_type="Project", sort_on="created", sort_order="reverse"
        )[:limit]


class RandomProjectsTile(BaseProjectsTile):
    """A tile that displays random projects"""

    def contents(self):
        limit = self.data["limit"]
        query = {}
        randomizer = TileRandomizer()
        query["sort_on"] = randomizer.random_sort_key
        query["sort_order"] = randomizer.random_sort_order
        result = api.content.find(portal_type="Project", **query)[:200]
        shuffle(result)
        return result[:limit]

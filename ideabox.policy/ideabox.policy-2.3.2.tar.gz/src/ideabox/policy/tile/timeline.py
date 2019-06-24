# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ideabox.policy import _
from plone.supermodel.model import Schema
from plone.tiles import Tile
from zope import schema


class ITimelineTile(Schema):
    """A tile that displays a listing of content items"""

    steps = schema.Text(
        title=_(u"Steps for timeline"),
        description=_(u"Title; Date; Link"),
        required=True,
    )


class TimelineTile(Tile):
    """A tile that displays a listing of content items"""

    template = ViewPageTemplateFile("templates/timeline.pt")

    def __call__(self):
        return self.template()

    def steps(self):
        steps = self.data["steps"]
        lines = steps.split("\r\n")
        data_steps = []
        for line in lines:
            data_line = line.split(";")
            if len(data_line) > 0 and len(data_line) < 4:
                step = {"title": "", "date": "", "link": ""}
                step["title"] = data_line[0]
                if len(data_line) > 1:
                    step["date"] = data_line[1]
                if len(data_line) > 2:
                    step["link"] = data_line[2]
                data_steps.append(step)
        return data_steps

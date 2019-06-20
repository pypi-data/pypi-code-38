# -*- coding: utf-8 -*-

from collective.gnd import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import provider


class IGndIdMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IGndId(model.Schema):
    """
    """

    gnd_id = schema.TextLine(
        title=_(u"GND-ID"),
        description=_(
            u"GND ID, see "
            u'<a href="https://www.wikidata.org/wiki/Property:P227"'
            u' target="_blank">https://www.wikidata.org/wiki/Property:P227</a>'
        ),
        required=False,
    )


@implementer(IGndId)
@adapter(IGndIdMarker)
class GndId(object):
    def __init__(self, context):
        self.context = context

    @property
    def gnd_id(self):
        return self.context.gnd_id

    @gnd_id.setter
    def gnd_id(self, value):
        self.context.gnd_id = value

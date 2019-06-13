from ftw.topics import _
from ftw.topics.interfaces import ITopic
from plone.dexterity.content import Container
from plone.directives.form import Schema
from zope import schema
from zope.interface import implements


class ITopicSchema(Schema):

    show_backrefs = schema.Bool(
        title=_(u"Show backreferences"),
        default=True,
        required=False
        )


class Topic(Container):
    implements(ITopic)

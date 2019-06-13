from ftw.topics.interfaces import ITopicTree
from plone.dexterity.content import Container
from plone.directives.form import Schema
from zope.interface import implements


class ITopicTreeSchema(Schema):
    pass


class TopicTree(Container):
    implements(ITopicTree)

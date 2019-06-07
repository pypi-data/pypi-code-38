# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from collective.contentgroups import _
from collective.contentgroups.utils import list_users
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from Products.CMFPlone.utils import base_hasattr
from six import string_types
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IGroup(model.Schema):
    """
    """

    users = schema.Text(
        title=_(u"users_field_title", default=u"Users"),
        description=_(
            u"users_field_description",
            default=u"List the ids of users belonging to this group, one per line.",
        ),
        required=False,
    )


@implementer(IGroup)
@adapter(IDexterityContent)
class Group(object):

    security = ClassSecurityInfo()
    security.declareObjectPrivate()

    def __init__(self, group):
        self.group = group

    @property
    def users(self):
        # I am tempted to return list_users(self.group),
        # but then you literally see a list in the view and the edit form.
        # This would help: "\n".join(list_users(self.group))
        # But let's simply return what we have.
        if base_hasattr(self.group, "users"):
            return self.group.users
        return ""

    @users.setter
    def users(self, value):
        # First make sure we have a proper list.
        if not isinstance(value, (list, tuple)):
            if not isinstance(value, string_types):
                value = str(value)
            value = list_users(value)
        # Then turn it into a string again.
        value = "\n".join(filter(None, value))
        self.group.users = value

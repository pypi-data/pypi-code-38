# -*- coding: utf-8 -*-

from ideabox.policy import _
from plone import schema
from plone.app.users.browser.register import BaseRegistrationForm
from plone.app.users.browser.userdatapanel import UserDataPanel
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible
from z3c.form import field
from z3c.form.browser.radio import RadioFieldWidget
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IEnhancedUserDataSchema(model.Schema):

    last_name = schema.TextLine(title=_(u"Last name or institution"), required=True)

    first_name = schema.TextLine(title=_(u"First name"), required=False)

    address = schema.Text(title=_(u"Address"), required=False)

    gender = schema.Choice(
        title=_(u"Gender"), required=True, vocabulary=u"ideabox.vocabularies.gender"
    )

    birthdate = schema.Date(title=_(u"Birthdate"), required=True)

    zip_code = schema.Choice(
        title=_(u"Zip code"), required=True, vocabulary=u"ideabox.vocabularies.zip_code"
    )

    iam = schema.Choice(
        title=_(u"I am"), required=True, vocabulary=u"collective.taxonomy.iam"
    )


class UserDataPanelExtender(extensible.FormExtender):
    adapts(Interface, IDefaultBrowserLayer, UserDataPanel)

    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        fields = fields.omit("accept")
        fields["gender"].widgetFactory = RadioFieldWidget
        self.add(fields)


class RegistrationPanelExtender(extensible.FormExtender):
    adapts(Interface, IDefaultBrowserLayer, BaseRegistrationForm)

    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        fields["gender"].widgetFactory = RadioFieldWidget
        self.add(fields)

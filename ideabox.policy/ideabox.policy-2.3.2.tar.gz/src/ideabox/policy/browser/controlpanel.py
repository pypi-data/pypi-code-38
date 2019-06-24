# -*- coding: utf-8 -*-

from ideabox.policy import _
from plone.app.registry.browser import controlpanel
from zope import schema
from zope.interface import Interface


class InvalidEmailError(schema.ValidationError):
    __doc__ = u"Please enter a valid e-mail address."


class IIdeaBoxSettingsSchema(Interface):

    project_manager_email = schema.TextLine(
        title=_(u"Email address of the project manager"),
        description=_(
            u"If there are multiple email addresses, separate them with semicolons"
        ),
    )

    project_submission = schema.Bool(
        title=_(u"Enable / Disable project submission"), default=True
    )


class IdeaBoxSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IIdeaBoxSettingsSchema
    label = _(u"Configuration for ideabox product")
    description = _(u"")

    def updateFields(self):
        super(IdeaBoxSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(IdeaBoxSettingsEditForm, self).updateWidgets()


class IdeaBoxSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = IdeaBoxSettingsEditForm

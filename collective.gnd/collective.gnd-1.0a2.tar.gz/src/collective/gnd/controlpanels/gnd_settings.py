from collective.gnd import _
from plone.app.registry.browser import controlpanel
from plone.z3cform import layout
from Products.Five.browser import BrowserView
from zope import schema
from zope.interface import Interface


class IGndSettings(Interface):
    """ Define settings data structure for registry"""

    message = schema.TextLine(
        title=_(u"Message"),
        description=_(u""),
        default=u"My Portal",
        required=False,
        readonly=False,
    )

    contact = schema.TextLine(
        title=_(u"Contact"),
        description=_(u""),
        default=u"firstname lastname <jane@example.com>",
        required=False,
        readonly=False,
    )

    institution = schema.TextLine(
        title=_(u"Institution"),
        description=_(u""),
        default=u"",
        required=False,
        readonly=False,
    )

    description = schema.TextLine(
        title=_(u"Description"),
        description=_(u""),
        default=u"",
        required=False,
        readonly=False,
    )


class GndSettingsEditForm(controlpanel.RegistryEditForm):
    """
    """

    schema = IGndSettings
    label = u"GND Settings"


GndSettingsView = layout.wrap_form(
    GndSettingsEditForm, controlpanel.ControlPanelFormWrapper)

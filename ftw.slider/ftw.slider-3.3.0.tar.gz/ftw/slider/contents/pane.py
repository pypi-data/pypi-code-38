from ftw.referencewidget.widget import ReferenceWidgetFactory
from ftw.slider import _
from ftw.slider.interfaces import IPane
from pkg_resources import get_distribution
from plone.app.textfield import RichText
from plone.dexterity.content import Container
from plone.directives import form
from plone.directives.form import Schema
from plone.namedfile.field import NamedImage
from plone.supermodel import model
from zope import schema
from zope.interface import Invalid
from zope.interface import implements
from zope.interface.interface import invariant


IS_PLONE_5 = get_distribution('Plone').version >= '5'

if not IS_PLONE_5:
    from plone.app.dexterity import PloneMessageFactory as _PMF
else:
    from Products.CMFPlone import PloneMessageFactory as _PMF


class IPaneSchema(Schema):

    title = schema.TextLine(
        title=_PMF(u'label_title', default=u'Title'),
        required=True
        )

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        required=False,
        default=False,
        missing_value=False,
    )

    text = RichText(
        title=_(u'label_text', default=u'Text'),
        description=_(u'help_text', default=u''),
        required=False,
        )

    model.primary('image')
    image = NamedImage(
        title=_(u'label_image', default='Image'),
        required=True,
        )

    image_alt_text = schema.TextLine(
        title=_(u'label_image_alt_text', default=u'Image alt text'),
        required=False
        )

    form.widget(link=ReferenceWidgetFactory)
    link = schema.TextLine(
        title=_(u'label_link', default=u'Link'),
        description=_(u'help_link', default=u''),
        required=False,
        )

    external_url = schema.URI(
        title=_(u'label_external_url', default=u'External URL'),
        required=False,
    )

    @invariant
    def validate_links(data):
        """
        It is not allowed to add a link and an external url at the same time.
        """
        if data.link and data.external_url:
            raise Invalid(_(
                u'error_message_links',
                default=u'It\'s not possible to add a link and an '
                        u'external url at the same time')
            )


class Pane(Container):
    implements(IPane)

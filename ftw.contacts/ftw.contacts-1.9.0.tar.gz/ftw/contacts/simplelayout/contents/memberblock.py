from collective import dexteritytextindexer
from ftw.contacts import _
from ftw.contacts.interfaces import IMemberBlock
from ftw.contacts.simplelayout.interfaces import IMemberRegistry
from ftw.contacts.utils import get_organization
from ftw.referencewidget.widget import ReferenceBrowserWidget
from plone.dexterity.content import Item
from plone.directives.form import widget
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.relationfield.schema import Relation
from z3c.schema.email import RFC822MailAddress
from zope import schema
from zope.component import getUtility
from zope.interface import implements


def get_address_root(widget):
    registry = getUtility(IRegistry).forInterface(IMemberRegistry)
    path = registry.member_nav_tree_query_path or ''

    if not path:
        path = '/'.join(widget.context.getPhysicalPath())
    return path


class IMemberBlockSchema(model.Schema):
    """A member type schema interface
    """
    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        missing_value=u"",
        default=u"",
        required=False)

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        required=False)

    widget('contact', ReferenceBrowserWidget, start=get_address_root,
           override=True, selectable=['ftw.contacts.Contact'])
    contact = Relation(
        title=_(u'label_contact_reference', default=u'Contact reference'),
        required=True)

    dexteritytextindexer.searchable('function')
    function = schema.TextLine(
        title=_(u'label_function', default=u'Function'),
        missing_value=u"",
        default=u"",
        required=False)

    show_address = schema.Bool(
        title=_(u'label_show_address', default=u'Show address'),
        required=False)

    show_image = schema.Bool(
        title=_(u'label_show_image', default=u'Show image'),
        required=False)

    acquire_address = schema.Bool(
        title=_(u'label_acquire_address', default=u'Acquire address'),
        required=True)

    dexteritytextindexer.searchable('address')
    address = schema.Text(
        title=_(u'label_address', default=u'Address'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('postal_code')
    postal_code = schema.TextLine(
        title=_(u'label_postal_code', default=u'Postal code'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('city')
    city = schema.TextLine(
        title=_(u'label_city', default=u'City'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('email')
    email = RFC822MailAddress(
        title=_(u'label_email', default=u'E-Mail'),
        missing_value=u"",
        required=False)

    dexteritytextindexer.searchable('phone_office')
    phone_office = schema.TextLine(
        title=_(u'label_phone_office', default=u'Office phone number'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('phone_mobile')
    phone_mobile = schema.TextLine(
        title=_(u'label_phone_mobile', default=u'Mobile phone number'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('fax')
    fax = schema.TextLine(
        title=_(u'label_fax', default=u'Fax number'),
        missing_value=u"",
        default=u"",
        required=False)

    www = schema.URI(
        title=_(u'label_www', default=u'www'),
        missing_value=u"",
        required=False)

    model.fieldset(
        'contact',
        label=_(u'label_fieldset_contact', default=u"Contact"),
        fields=[
            'show_image',
            'acquire_address',
            'address',
            'postal_code',
            'city',
            'phone_office',
            'phone_mobile',
            'fax',
            'email',
            'www']
    )


class MemberBlock(Item):
    """A member
    """
    implements(IMemberBlock)

    def organization(self):
        return get_organization(
            self, ['OrgUnit', 'ftw.simplelayout.ContentPage'])

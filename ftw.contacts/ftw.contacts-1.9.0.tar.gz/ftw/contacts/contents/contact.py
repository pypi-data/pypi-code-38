from collective import dexteritytextindexer
from ftw.contacts import _
from ftw.contacts.interfaces import IContact
from ftw.contacts.utils import get_contact_title
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from z3c.schema.email import RFC822MailAddress
from zope import schema
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class NoOrganizationOrFullname(Invalid):
    """The organization or fullname is invalid
    """


gender_choice_vocabulary = SimpleVocabulary([
    SimpleTerm(value=u'm', title=_(u'label_male', default=u'Male')),
    SimpleTerm(value=u'f', title=_(u'label_female', default=u'Female')),
    SimpleTerm(value=u'', title=_(u'label_gender_neutral', default=u'-'))
    ])


class IContactSchema(model.Schema):
    """A contact type schema interface
    """
    dexteritytextindexer.searchable('organization')
    organization = schema.TextLine(
        title=_(u'label_organization', default=u'Organization'),
        missing_value=u"",
        default=u"",
        required=False)

    gender = schema.Choice(
        title=_(u'label_gender', default=u'Gender'),
        vocabulary=gender_choice_vocabulary,
        required=True,
        default="")

    dexteritytextindexer.searchable('lastname')
    lastname = schema.TextLine(
        title=_(u'label_lastname', default=u'Lastname'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('firstname')
    firstname = schema.TextLine(
        title=_(u'label_firstname', default=u'Firstname'),
        missing_value=u"",
        default=u"",
        required=False)

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

    directives.mode(country='hidden')
    country = schema.TextLine(
        title=_(u'label_country', default=u'Country'),
        required=False,
        default=u"Schweiz")

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

    image = NamedBlobImage(
        title=_(u'label_image', default=u'Image'),
        missing_value=None,
        required=False)

    academic_title = schema.TextLine(
        title=_(u'label_academic_title', default=u'Academic title'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('function')
    function = schema.TextLine(
        title=_(u'label_function', default=u'Function'),
        description=_(
            u'description_function',
            default=u'Will be displayed even if the address is '
                    u'acquired and the contact has a function.'
        ),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('department')
    department = schema.TextLine(
        title=_(u'label_department', default=u'Department'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('salutation')
    salutation = schema.TextLine(
        title=_(u'label_salutation', default=u'Salutation'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('text')
    text = RichText(
        title=_(u'label_text', default=u'Text'),
        required=False,
        allowed_mime_types=('text/html',))

    dexteritytextindexer.searchable('phone_private')
    phone_private = schema.TextLine(
        title=_(u'label_phone_private', default=u'Private phone number'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('address_private')
    address_private = schema.Text(
        title=_(u'label_address_private', default=u'Address'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('postal_code_private')
    postal_code_private = schema.TextLine(
        title=_(u'label_postal_code_private', default=u'Postal code'),
        missing_value=u"",
        default=u"",
        required=False)

    dexteritytextindexer.searchable('city_private')
    city_private = schema.TextLine(
        title=_(u'label_city_private', default=u'City'),
        missing_value=u"",
        default=u"",
        required=False)

    directives.mode(uid='hidden')
    uid = schema.TextLine(
        title=_(u'label_uid', default=u'UID'),
        missing_value=u"",
        default=u"",
        required=False)

    directives.mode(ldap_dn='hidden')
    ldap_dn = schema.TextLine(
        title=_(u'label_ldap_dn', default=u'LDAP DN'),
        missing_value=u"",
        default=u"",
        required=False)

    hide_memberships = schema.Bool(
        title=_(u'label_hide_memberships', default=u'Hide memberships'),
        default=False,
        required=False)

    hide_map = schema.Bool(
        title=_(u'label_hide_map', default=u'Hide map'),
        default=False,
        required=False)

    model.fieldset(
        'extended',
        label=_(u'label_fieldset_extended', default=u"Extended"),
        fields=[
            'image',
            'academic_title',
            'function',
            'department',
            'salutation',
            'text',
            'hide_memberships',
            'hide_map',
        ]
    )

    model.fieldset(
        'private',
        label=_(u'label_fieldset_homeaddress', default=u"Home address"),
        fields=[
            'phone_private',
            'address_private',
            'postal_code_private',
            'city_private']
    )

    @invariant
    def validateOrganizationOrFullname(data):
        if data.organization or (data.firstname and data.lastname):
            return None

        raise NoOrganizationOrFullname(_(
            u'validation_error_organization_or_name_required',
            default=u'Either the name of the organization or first- '
            u'and lastname of the person is required.')
        )


class Contact(Item):
    """A contact
    """
    implements(IContact)

    @property
    def title(self):
        """Getter function for the title

        The contact title is generated from the firstname and lastname
        or from the organization name. Depends on what fields are filled.
        """
        return get_contact_title(self)

    def setTitle(self, value):
        return

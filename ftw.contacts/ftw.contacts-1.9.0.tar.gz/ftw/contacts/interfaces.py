from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope import schema


_ = MessageFactory('plone')


class IMemberAccessor(Interface):
    """Generic member accessor adapter implementation for Dexterity content
       objects.
    """


class IContactFolder(Interface):
    """
    """


class IContact(Interface):
    """
    """


class IMemberBlock(Interface):
    """
    """


class ILDAPAttributeMapper(Interface):
    """A utility that provides the mapping between LDAP attributes and
       Dexterity fields.
    """
    def mapping():
        """Returns a mapping of LDAP attibute names -> DX field names.
        """

    def id():
        """Returns the name of the LDAP attribute name used as contact id.
        """


class ILDAPCustomUpdater(Interface):
    """An adapter for updating a contact object with custom data.
       Adapts a contact object and the related ldap record.
    """
    def update():
        """Updates the adapted contact object. Returns true if the object was
           modified.
        """


class ILDAPSearch(Interface):
    """Utility for searching in LDAP.
    """


class IContactsSettings(Interface):
    """Registry entries for ftw.contacts"""

    ldap_plugin_id = schema.TextLine(
        title=_(u'LDAP Plugin ID'),
        description=_(u'ID of the LDAP PAS plugin to use '
                      u'for contact synchronisation'),
        default=None,
        required=False)

    contacts_path = schema.TextLine(
        title=_(u'Contacts Path'),
        description=_(u'Path to the folder containing contacts'),
        default=None,
        required=False)

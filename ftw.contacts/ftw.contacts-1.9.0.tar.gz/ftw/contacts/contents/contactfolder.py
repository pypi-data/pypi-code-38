from ftw.contacts import _
from ftw.contacts.interfaces import IContactFolder
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements


class IContactFolderSchema(model.Schema):
    """A contactfolder type schema interface
    """

    hide_contacts_image = schema.Bool(
        title=_(u'label_contactdirectory_hide_contacts_image',
                default=u'Hide images of contacts'),
        default=False,
        description=_(u'help_contactdirectory_hide_contacts_image',
                      default=u'If activated, the images of the contacts are not shown in the listing-view.')
    )


class ContactFolder(Container):
    """A contactfolder
    """
    implements(IContactFolder)

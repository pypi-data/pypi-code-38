from ftw.contacts.interfaces import IContact
from ftw.contacts.utils import generate_vcard
from ftw.zipexport.interfaces import IZipRepresentation
from ftw.zipexport.representations.general import NullZipRepresentation
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class ContactZipRepresentation(NullZipRepresentation):
    implements(IZipRepresentation)
    adapts(IContact, Interface)

    def get_files(self, path_prefix=u"", recursive=True, toplevel=True):
        filename = safe_unicode('{0}.vcf'.format(self.context.getId()))

        yield (u'{0}/{1}'.format(safe_unicode(path_prefix), filename),
               generate_vcard(self.context))

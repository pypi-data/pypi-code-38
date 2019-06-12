from Acquisition import aq_inner
from Acquisition import aq_parent
from base64 import b64encode
from plone import api
from plone.memoize import instance
from plone.namedfile.utils import stream_data
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from StringIO import StringIO
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import unicodedata


ALPHABET = map(chr, range(ord('A'), ord('Z') + 1))
LETTERS = ALPHABET + ['#']


def encode(text):
    if not text:
        return ''
    if isinstance(text, unicode):
        return text.encode('utf-8')
    return text


def get_organization(context, portal_types=[]):
    """Traverse up to search a parent-object matching a portal_type
    If it reaches a portal_type, it returns its title.
    If it reaches the plone siteroot it returns an empty string
    """
    context = aq_inner(context)
    parent = aq_parent(context)
    while parent.portal_type not in portal_types:
        if IPloneSiteRoot.providedBy(parent):
            return ''
        parent = parent.aq_parent
    return parent.Title()


def safe_html(text):
    if not text:
        return ''

    if isinstance(text, unicode):
        text = text.encode('utf-8')

    ttool = api.portal.get_tool('portal_transforms')
    text = ttool.convertTo('text/x-html-safe', text).getData()

    # we need html br
    text = text.replace('\r\n', '<br />').replace('\n', '<br />')

    # we dont want p tags
    text = text.replace('<p>', '').replace('</p>', '')

    return text


def get_backreferences(source_object, from_interface):
    """
    Return back references from source object on specified attribute_name
    """
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    mtool = api.portal.get_tool('portal_membership')

    result = []

    for rel in catalog.findRelations({
            'to_id': intids.getId(aq_inner(source_object)),
            'from_interfaces_flattened': from_interface}):

        obj = intids.queryObject(rel.from_id)

        if obj is not None and mtool.checkPermission('View', obj):
            result.append(obj)
    return result


def get_contact_title(contact, display=None):
    """This function returns the contacttitle.

    The contact title is generated from the firstname and lastname
    or from the organization name. Depends on what fields are filled.
    """

    if contact.firstname and contact.lastname:
        if display == 'natural':
            return '%s %s' % (contact.firstname, contact.lastname)
        return '%s %s' % (contact.lastname, contact.firstname)
    return contact.organization or u"..."


def normalized_first_letter(text):
    """Normalizes the first letter of the text
    """
    text = make_sortable(text)
    return text[0].upper()


def make_sortable(text):
    """Makes the text sortable
    """
    text = text.lower()
    text = text.decode('utf-8')
    normalized = unicodedata.normalize('NFKD', text)
    text = u''.join(
        [c for c in normalized if not unicodedata.combining(c)])
    text = text.encode('utf-8')
    return text


class AlphabeticLetters(object):
    """Provides a function to generate letters with different attributes
    """
    def letters(self, current_letter, brains):
        """Returns a dict with all available letters and
        aditional infos for each letter.

        The dict has:

        label: the letter name
        has_contents: css-class if there are objs with the letter
        current: css-class if the letter is the current letter
        """
        letters_with_content = self._letters_with_content(brains)

        for letter in LETTERS:
            has_contents = letter in letters_with_content and \
                "withContent" or ''
            current = letter == current_letter and 'active' or ''
            yield {'label': letter,
                   'has_contents': has_contents,
                   'current': current}

    @instance.memoize
    def _letters_with_content(self, brains):
        letters = set([])
        for contactname in [brain.Title for brain in brains]:
            first_letter = normalized_first_letter(contactname)
            if first_letter in ALPHABET:
                letters.add(first_letter)
            else:
                letters.add('#')

        return sorted(letters, key=LETTERS.index)


def generate_vcard(contact):
    # TODO: Refactoring
    io = StringIO()

    gender_map = {
        'm': 'M',
        'f': 'F',
        '': 'U'
    }

    def addProp(name, value):
        if not value:
            return
        io.write('{0}:{1}\n'.format(encode(name), encode(value)))

    addProp('BEGIN', 'VCARD')
    addProp('VERSION', '3.0')
    addProp('N', '{0};{1};;{2}'.format(encode(contact.lastname),
                                       encode(contact.firstname),
                                       encode(contact.salutation)))
    addProp('FN', encode(contact.title))
    addProp('GENDER', gender_map.get(encode(contact.gender), ''))
    addProp('ORG', encode(contact.organization))
    addProp('ADR;TYPE=WORK', ';;{0};{1};;{2};{3}'.format(
        encode(contact.address.replace('\n', '\\n').replace('\r', '')),
        encode(contact.city),
        encode(contact.postal_code),
        encode(contact.country)))
    addProp('EMAIL', encode(contact.email))
    addProp('TEL;TYPE=WORK', encode(contact.phone_office))
    addProp('TEL;TYPE=WORK;TYPE=CELL', encode(contact.phone_mobile))
    addProp('TEL;TYPE=WORK;TYPE=FAX', encode(contact.fax))
    addProp('URL', encode(contact.www))
    addProp('ROLE', encode(contact.function))
    addProp('TEL;TYPE=HOME', encode(contact.phone_private))
    addProp('ADR;TYPE=HOME', ';;{0};{1};;{2};'.format(
        encode(contact.address_private.replace(
            '\r\n', '\\n').replace('\r', '')),
        encode(contact.city_private),
        encode(contact.postal_code_private)))

    if contact.image:
        imgdata = StringIO()
        imgdata.write(stream_data(contact.image))
        addProp('PHOTO;ENCODING=B', b64encode(imgdata.getvalue()))

    addProp('END', 'VCARD')
    io.seek(0)

    return io

def portrait_img_tag(contact):
    scaler = contact.restrictedTraverse('@@images')
    return scaler.scale('image', scale='portrait', direction='down').tag()

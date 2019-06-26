from zope.interface import Interface
from zope import schema
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from emrt.necd.content import MessageFactory as _
from logging import getLogger
from collections import OrderedDict
logger = getLogger('emrt.necd.content.nfr_codes')


class INECDSettings(Interface):
    """Settings expected to be found in plone.registry
    """

    nfrcodeMapping = schema.Dict(
        title=_(u"NFR Codes"),
        description=_(u"Maps ldap sectors"),
        key_type=schema.TextLine(title=_(u"Code")),
        value_type=schema.TextLine(
            title=_(u"Sector Item"),
            description=_(
                u"Descripe a sector in the form: ldap|code|name|title")
        ),
    )

    nfrcodeMapping_projection = schema.Dict(
        title=_(u"NFR projection category codes"),
        description=_(u"Maps ldap sectors for Projection ReviewFolders"),
        key_type=schema.TextLine(title=_(u"Code")),
        value_type=schema.TextLine(
            title=_(u"Sector Item"),
            description=_(
                u"Describe a sector in the form: ldap|code|name|title")
        ),
    )

    nfrcodeMapping_projection_inventory = schema.Dict(
        title=_(u"NFR inventories category codes"),
        description=_(u"Maps ldap sectors for Projection ReviewFolders"),
        key_type=schema.TextLine(title=_(u"Code")),
        value_type=schema.TextLine(
            title=_(u"Sector Item"),
            description=_(
                u"Describe a sector in the form: ldap|code|name|title")
        ),
    )

    sectorNames = schema.Dict(
        title=_(u"Sector names"),
        description=_(u"Maps sector IDs to names"),
        key_type=schema.TextLine(title=_(u"Sector ID")),
        value_type=schema.TextLine(
            title=_(u"Sector name"),
        ),
    )


def map_nfr_codes(codes):
    nfr_codes = {}

    for key, codes in codes.items():
        try:
            ldap, code, name, title = codes.split('|')
            nfr_codes[key] = {
                "ldap": ldap,
                "code": code,
                "name": name,
                "title": title
            }
        except Exception:
            logger.warning('%s is not well formatted' % key)

    return nfr_codes


def nfr_codes(context, field=None):
    """ get the NFR code mapping from portal_registry
        @return a dictionary
        {
            "key": {
                "ldap": "sector",
                "code": "key",
                "name": "name",
                "title": "title"
            },
            ...
        }
    """
    registry = getUtility(IRegistry)
    nfrcodeInterface = registry.forInterface(INECDSettings)

    # Use "field" if specified, else check for projection context.
    field_name = field or (
        'nfrcodeMapping_projection' if context.type == 'projection'
        else 'nfrcodeMapping'
    )

    nfrcodeMapping = nfrcodeInterface.__getattr__(field_name)

    nfr_codes = map_nfr_codes(nfrcodeMapping)
    return OrderedDict(sorted(nfr_codes.items()))


def get_category_ldap_from_nfr_code(value, context):
    """ get the NFR category this NFR Code matches
        According to the rules previously set
        for LDAP Matching
    """
    nfrcodes = nfr_codes(context)
    return nfrcodes.get(value, {}).get('ldap', '')


def get_category_value_from_nfr_code(value, context):
    """ get the NFR category value to show it in the observation metadata """
    nfrcodes = nfr_codes(context)
    return nfrcodes.get(value, {}).get('title', '')

"""XSD types utils
"""


def get_xsd_types(namespace_prefix=''):
    """Returns the list of all supported XSD types

    Args:
        namespace_prefix:

    Returns:

    """
    if namespace_prefix != '':
        namespace_prefix += ':'
    return ["{0}anyType".format(namespace_prefix),
            "{0}string".format(namespace_prefix),
            "{0}normalizedString".format(namespace_prefix),
            "{0}token".format(namespace_prefix),
            "{0}duration".format(namespace_prefix),
            "{0}dateTime".format(namespace_prefix),
            "{0}time".format(namespace_prefix),
            "{0}date".format(namespace_prefix),
            "{0}gYearMonth".format(namespace_prefix),
            "{0}gYear".format(namespace_prefix),
            "{0}gMonthDay".format(namespace_prefix),
            "{0}gDay".format(namespace_prefix),
            "{0}gMonth".format(namespace_prefix),
            "{0}boolean".format(namespace_prefix),
            "{0}base64Binary".format(namespace_prefix),
            "{0}hexBinary".format(namespace_prefix),
            "{0}float".format(namespace_prefix),
            "{0}double".format(namespace_prefix),
            "{0}anyURI".format(namespace_prefix),
            "{0}QName".format(namespace_prefix),
            "{0}decimal".format(namespace_prefix),
            "{0}integer".format(namespace_prefix),
            "{0}nonPositiveInteger".format(namespace_prefix),
            "{0}negativeInteger".format(namespace_prefix),
            "{0}long".format(namespace_prefix),
            "{0}nonNegativeInteger".format(namespace_prefix),
            "{0}unsignedLong".format(namespace_prefix),
            "{0}positiveInteger".format(namespace_prefix),
            "{0}unsignedInt".format(namespace_prefix),
            "{0}unsignedShort".format(namespace_prefix),
            "{0}unsignedByte".format(namespace_prefix),
            "{0}long".format(namespace_prefix),
            "{0}int".format(namespace_prefix),
            "{0}short".format(namespace_prefix),
            "{0}byte".format(namespace_prefix)]


def get_xsd_numbers(namespace_prefix=''):
    """Returns a list of formatted xsd number types

    Args:
        namespace_prefix:

    Returns:

    """
    if namespace_prefix != '':
        namespace_prefix += ':'
    return [
        '{0}byte'.format(namespace_prefix),
        '{0}int'.format(namespace_prefix),
        '{0}integer'.format(namespace_prefix),
        '{0}long'.format(namespace_prefix),
        '{0}negativeInteger'.format(namespace_prefix),
        '{0}nonNegativeInteger'.format(namespace_prefix),
        '{0}nonPositiveInteger'.format(namespace_prefix),
        '{0}positiveInteger'.format(namespace_prefix),
        '{0}short'.format(namespace_prefix),
        '{0}unsignedLong'.format(namespace_prefix),
        '{0}unsignedInt'.format(namespace_prefix),
        '{0}unsignedShort'.format(namespace_prefix),
        '{0}unsignedByte'.format(namespace_prefix),
        '{0}float'.format(namespace_prefix),
        '{0}double'.format(namespace_prefix),
        '{0}decimal'.format(namespace_prefix)]


def get_xsd_floating_numbers(namespace_prefix=''):
    """Returns a list of formatted xsd floating number types

    Args:
        namespace_prefix:

    Returns:

    """
    if namespace_prefix != '':
        namespace_prefix += ':'
    return [
        '{0}float'.format(namespace_prefix),
        '{0}double'.format(namespace_prefix),
        '{0}decimal'.format(namespace_prefix)]

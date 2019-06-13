"""xml utils"""

import xml.dom.minidom as DOM

def xmlPrettyPrint(xmlString, indent=None):
    """
    Convenience function that receives a xml string
    and returns it pretty printed

    Args:
        xmlString (bytes): a bytes xml string
        indent (str, optional): space padding string. Defaults to None.

    Returns:
        str: pretty printed formmated xml string
    """

    i = "    "
    if indent is not None:
        i = indent

    xDoc = DOM.parseString(xmlString)

    if xDoc:
        xPretty = xDoc.toprettyxml(indent=i)

    return xPretty

"""XSD Tree operations on annotations
"""
from xml_utils.commons import constants as xml_utils_constants


def remove_annotations(xsd_tree):
    """Removes annotations from tree

    Args:
        xsd_tree:

    Returns:

    """
    # find all annotations
    annotations = xsd_tree.findall(".//{}annotation".format(xml_utils_constants.LXML_SCHEMA_NAMESPACE))
    for annotation in annotations:
        annotation.getparent().remove(annotation)

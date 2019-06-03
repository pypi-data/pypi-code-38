""" XML utils
"""

from django.contrib.staticfiles import finders

from core_main_app.utils.xml import xsl_transform
from core_parser_app.settings import MODULE_TAG_NAME
from xml_utils.commons.constants import SCHEMA_NAMESPACE
from xml_utils.xsd_tree.operations.namespaces import get_global_namespace


def transform_xsd_to_html_with_modules(xsd_string):
    """ Convert xsd string with modules to html.

    Args:
        xsd_string:

    Returns:

    """
    # Get path to XSLT file
    xslt_path = finders.find('core_parser_app/xsl/xsd2html4modules.xsl')

    # get global namespace used in the schema
    global_namespace = get_global_namespace(xsd_string)
    # if a global namespace is present in the schema
    if global_namespace:
        # if the global namespace is the schema namespace
        if global_namespace == SCHEMA_NAMESPACE:
            # a prefix for this namespace is already present in the XSLT
            # FIXME: xsd prefix hardcoded here based on what is in the XSLT file.
            module_tag_name = "xsd:{0}".format(MODULE_TAG_NAME)
        else:
            # the schema is using a global namespace and it's not the XML Schema namespace
            # FIXME: to support this case, we would need to add a namespace prefix to the XSLT
            raise NotImplementedError("The schema is using an unsupported global namespace.")
    else:
        # no global namespace used
        module_tag_name = MODULE_TAG_NAME

    return xsl_transform(xsd_string, read_and_update_xslt_with_settings(xslt_path, module_tag_name))


def read_and_update_xslt_with_settings(xslt_file_path, module_tag_name):
    """Read the content of a file, and update it with the settings

    Args:
        xslt_file_path:
        module_tag_name:

    Returns:

    """
    with open(xslt_file_path) as xslt_file:
        # read the XSLT file
        xslt_file_content = xslt_file.read()
        # update the file with the desired module tag name
        xslt_file_content = xslt_file_content.replace("module_tag_name", module_tag_name)
        # return the updated file content
        return xslt_file_content

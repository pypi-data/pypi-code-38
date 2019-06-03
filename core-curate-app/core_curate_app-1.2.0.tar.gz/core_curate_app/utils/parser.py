"""Parser util for curate app
"""

from core_curate_app.settings import PARSER_MIN_TREE, PARSER_IGNORE_MODULES, PARSER_COLLAPSE, PARSER_AUTO_KEY_KEYREF, \
    PARSER_IMPLICIT_EXTENSION_BASE, PARSER_DOWNLOAD_DEPENDENCIES
from core_parser_app.tools.parser.parser import XSDParser


def get_parser():
    """Load configuration for the parser.

    Returns:

    """

    return XSDParser(min_tree=PARSER_MIN_TREE,
                     ignore_modules=PARSER_IGNORE_MODULES,
                     collapse=PARSER_COLLAPSE,
                     auto_key_keyref=PARSER_AUTO_KEY_KEYREF,
                     implicit_extension_base=PARSER_IMPLICIT_EXTENSION_BASE,
                     download_dependencies=PARSER_DOWNLOAD_DEPENDENCIES)
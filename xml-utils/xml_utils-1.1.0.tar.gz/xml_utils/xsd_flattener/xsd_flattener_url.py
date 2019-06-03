"""XSD Flattener URL class
"""

import urllib2
from xml_utils.xsd_flattener.xsd_flattener import XSDFlattener


class XSDFlattenerURL(XSDFlattener):
    """XSD Flattener class getting dependencies by URL
    """

    def __init__(self, xml_string, download_enabled=True):
        """ Initialize the flattener

        Args:
            xml_string:
            download_enabled:
        """
        XSDFlattener.__init__(self, xml_string=xml_string)
        self.download_enabled = download_enabled

    def get_dependency_content(self, uri):
        """ Download the content found at the URL

        Args:
            uri:

        Returns:

        """
        content = ""

        if self.download_enabled:
            dependency_file = urllib2.urlopen(uri)
            content = dependency_file.read()

        return content

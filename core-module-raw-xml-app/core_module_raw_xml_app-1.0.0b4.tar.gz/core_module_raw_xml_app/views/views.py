""" Raw Xml module
"""
import HTMLParser

from core_module_text_area_app.views.views import TextAreaModule
from xml_utils.commons.exceptions import XMLError
from xml_utils.xsd_tree.xsd_tree import XSDTree


class RawXmlModule(TextAreaModule):
    parser = None

    def __init__(self):
        """ Initialize RawXmlModule
        """
        self.parser = HTMLParser.HTMLParser()
        TextAreaModule.__init__(self, label="Raw XML", data="Insert XML Data here...")

    def _retrieve_data(self, request):
        """ Retrieve module's data

        Args:
            request:

        Returns:

        """
        data = ''
        if request.method == 'GET':
            if 'data' in request.GET:
                data = request.GET['data']
                try:
                    xml_string = ''
                    # convert the string to an XML tree
                    xml_data = self.parse_data_with_root(data)
                    for xml_data_element in xml_data:
                        # keep the pretty format of the XML for display
                        xml_string += XSDTree.tostring(xml_data_element, True)
                    data = xml_string if xml_string else request.GET['data']
                except XMLError:
                    # If an XML Error is thrown when we want to display the data again
                    # the data may not be valid
                    # so we display the data as is
                    data = request.GET['data']

        elif request.method == 'POST':
            if 'data' in request.POST:
                data = request.POST['data']

        return data

    def _render_data(self, request):
        """ Return module's data rendering

        Args:
            request:

        Returns:

        """
        if self.data == '':
            return '<span class="alert-info">Please enter XML in the text area located above</span>'
        try:
            # parse the data
            self.parse_data_with_root(self.data)
            return '<span class="alert-success">XML entered is well-formed</span>'
        except XMLError, ex:
            return '<span class="alert-danger">XML error: ' + ex.message + '</span>'

    def parse_data_with_root(self, data):
        """ Parse the xml and add a root to it for validation

        Args:
            data:

        Returns:

        """
        unescaped_data = self.parser.unescape(data)
        # concat a root to the entry, then parse the string to a tree and return it
        return XSDTree.fromstring(''.join(['<root>', unescaped_data, '</root>']))

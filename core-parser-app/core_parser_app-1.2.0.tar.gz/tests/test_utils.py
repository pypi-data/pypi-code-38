""" Testing utils
"""
import collections
import json
from os.path import join

from lxml import etree

from xml_utils.xsd_tree.xsd_tree import XSDTree


class DataHandler:
    def __init__(self, dir_name):
        """ Init data handler
        """
        self.dir_name = dir_name

    @staticmethod
    def get_xml_file(filename):
        """ Get XML file

        Args:
            filename:

        Returns:

        """
        file_string = ''
        is_in_tag = False

        with open(filename, 'r') as file_content:
            file_lines = [line.strip('\r\n\t ') for line in file_content.readlines()]

            for line in file_lines:
                if is_in_tag:  # Add space if we are in the tag
                    file_string += ' '

                file_string += line

                # Leave the tag if we have one more closing that opening
                if is_in_tag and line.count('>') == line.count('<') + 1:
                    is_in_tag = False
                elif line.count('<') != line.count('>'):  # In tag if opening and closing count are different
                    is_in_tag = True

                # In any other cases the tag flag doesn't change

        return XSDTree.fromstring(file_string)

    def get_xml(self, filename):
        """ Get XML

        Args:
            filename:

        Returns:

        """
        filename = join(self.dir_name, filename + '.xml')
        return etree.ElementTree(self.get_xml_file(filename))

    def get_xsd(self, filename):
        """ Get XSD

        Args:
            filename:

        Returns:

        """
        filename = join(self.dir_name, filename + '.xsd')
        return etree.ElementTree(self.get_xml_file(filename))

    def get_html(self, filename):
        """ Get HTML

        Args:
            filename:

        Returns:

        """
        filename = join(self.dir_name, filename + '.html')
        return self.get_xml(filename)

    def get_json(self, filename):
        """ Get JSON

        Args:
            filename:

        Returns:

        """
        filename = join(self.dir_name, filename + '.json')
        with open(filename, 'r') as json_file:
            json_data = json.load(json_file, encoding='utf-8')

        return convert(json_data)


def convert(data):
    """ Convert data

    Args:
        data:

    Returns:

    """
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

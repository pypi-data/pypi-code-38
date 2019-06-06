from .abstractalephmarcreader import AbstractAlephMarcReader
import sys
from lxml import etree


class AlephXReader(AbstractAlephMarcReader):
    """
        Represents the root element of a parsed MarcXML file.
        :param etree.ElementTree __root root element of a parsed MarcXML file..
        """

    def __init__(self, file_path):
        """
        :param str file_path: the path to the MarcXML file.
        """
        super(AlephXReader, self).__init__('1')
        self.__root = self.__parseMarcXML(file_path)

    def __parseMarcXML(self, file_path):
        """
        Returns the root element of a parsed MarcXML file.
        :param str file_path: the path to the MarcXML file.
        :return: etree.ElementTree
        """
        try:
            tree = etree.parse(file_path)
            return tree
        except Exception as e:
            sys.stderr.write("Parsing MarcXML failed for " + file_path + " " + str(e))
            raise
    __parseMarcXML.__annotations__ = {'file_path': str, 'return': etree.ElementTree}

    def _AbstractAlephMarcReader__get_subfield_texts(self, marc_ele, index):
        """
        Given a marc field, get the indicated subfield's text or False if it does not exist.
        :param marc_ele: marc field.
        :param index: index of the subfield.
        :return: [str].
        """
        eles = marc_ele.xpath(".//subfield[@label='" + index + "']")
        return list(map(lambda ele: ele.text, eles))
    _AbstractAlephMarcReader__get_subfield_texts.__annotations__ = {'index': str, 'marc_ele': etree.Element, 'return': [str]}

    def _AbstractAlephMarcReader__get_field(self, index):
        """
        Returns marc fields corresponding to the given index.
        :param index: index of marc field.
        :return: [etree.Element]
        """
        elements = self.__root.xpath(".//varfield[@id='" + index + "']")
        return elements
    _AbstractAlephMarcReader__get_field.__annotations__ = {'index': str, 'return': [etree.Element]}
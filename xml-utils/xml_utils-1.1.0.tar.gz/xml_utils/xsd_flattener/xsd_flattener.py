""" XSD Flattener abstract class
"""
from xml_utils.xsd_tree.xsd_tree import XSDTree
import lxml.etree as etree
from abc import ABCMeta, abstractmethod
import xml_utils.commons.constants as constants


class XSDFlattener(object):
    """ Abstract XSD Flattener class
    """
    __metaclass__ = ABCMeta

    def __init__(self, xml_string, download_enabled=True):
        """ Initializes the flattener

        Args:
            xml_string:
            download_enabled:
        """
        self.xml_string = xml_string
        self.dependencies = []
        self.download_enabled = download_enabled
        self.xsd_tree = XSDTree()

    def get_flat(self):
        """ Returns the flattened file

        Returns:

        """
        # builds the parser
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        # sets the parser
        etree.set_default_parser(parser=parser)

        # parse the XML String removing blanks, comments, processing instructions
        xml_tree = XSDTree.build_tree(self.xml_string)

        # replace the includes by their content
        return self._replace_all_includes_by_content(xml_tree)

    def get_flat_dependency(self, uri):
        """

        Args:
            uri:

        Returns:

        """
        try:
            # if the same uri has not already been added to the main tree
            if uri not in self.dependencies:
                self.dependencies.append(uri)
                # get the content of the dependency
                dependency_content = self.get_dependency_content(uri)
                # build the tree
                xml_tree = XSDTree.build_tree(dependency_content)
                # replace the includes by their content
                return self._replace_all_includes_by_content(xml_tree)
            else:
                return None
        except:
            return None

    def _replace_all_includes_by_content(self, xml_tree):
        """ Replace all includes by their content

        Args:
            xml_tree:

        Returns:

        """
        # get the includes
        includes = xml_tree.findall("{}include".format(constants.LXML_SCHEMA_NAMESPACE))
        # check if it has includes
        if len(includes) > 0:
            # browse includes
            for include_element in includes:
                # get the schema location uri
                uri = include_element.attrib['schemaLocation']
                # get the flattened dependency
                flat_dependency = self.get_flat_dependency(uri)
                # replace the include by its content
                XSDFlattener._replace_include_by_content(xml_tree, include_element, flat_dependency)
        return XSDTree.tostring(xml_tree)

    @staticmethod
    def _replace_include_by_content(xml_tree, include_element, dependency_content):
        """ Replace an include by its content

        Args:
            xml_tree:
            include_element:
            dependency_content:

        Returns:

        """
        if dependency_content is not None:
            # build the tree of the dependency
            dependency_tree = XSDTree.fromstring(dependency_content)
            # get elements from dependency
            dependency_elements = dependency_tree.getchildren()
            # appends elements from dependency to tree
            for element in dependency_elements:
                xml_tree.getroot().append(element)
        # remove the include element
        include_element.getparent().remove(include_element)

    @abstractmethod
    def get_dependency_content(self, uri):
        """

        Args:
            uri:

        Returns:

        """
        pass

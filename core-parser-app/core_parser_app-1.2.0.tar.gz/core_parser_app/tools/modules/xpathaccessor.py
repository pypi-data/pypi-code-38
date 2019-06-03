"""Xpath accessor class
"""

from abc import ABCMeta, abstractmethod
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.components.data_structure import api as data_structure_api


class XPathAccessor(object):
    __metaclass__ = ABCMeta
    
    def __init__(self, request):
        try:
            element = data_structure_element_api.get_by_id(request.POST['module_id'])

            self.xpath = element.options['xpath']['xml']
            self.values = {}
            self.set_XpathAccessor(request)
        except Exception, e:
            message = 'XPathAccessor error: '
            raise XPathAccessorError(message + e.message)

    def get_xpath(self):
        return self.xpath

    def set_xpath_value(self, form_id, xpath, value):
        root_id = data_structure_api.get_by_id(form_id).data_structure_element_root.id
        form_element = self._get_element(root_id, xpath)
        input_element = self.get_input(form_element)

        if input_element.tag != 'module':
            input_element.update(set__value=value)
        else:  # Element is a module
            options = input_element.options

            if 'data' in value:
                options['data'] = value['data']

            if 'attributes' in value:
                options['attributes'] = value['attributes']

            input_element.update(set__options=options)

        input_element.reload()

    def get_input(self, element):
        input_elements = ['input', 'restriction', 'choice', 'module']

        if element.tag in input_elements:
            return element

        for child in element.children:
            return self.get_input(child)

    def _get_element(self, form_id, xpath):
        form_root = data_structure_element_api.get_by_id(form_id)

        if self.element_has_xpath(form_root, xpath):
            return form_root

        if len(form_root.children) == 0:
            return None

        for child in form_root.children:
            element = self._get_element(child.pk, xpath)

            if element is not None:
                return element

    @staticmethod
    def element_has_xpath(element, xpath):
        return 'xpath' in element.options and element.options['xpath']['xml'] == xpath
    
    @abstractmethod
    def set_XpathAccessor(self, request):
        """ Set xpath accessor

        Args:
            request: HTTP request
        """
        raise NotImplementedError("This method is not implemented.")  
    
    def get_XpathAccessor(self):
        """Return xpath accessor values

        Returns:

        """
        return {'xpath_accessor': self.values}


class XPathAccessorError(Exception):
    """
        Exception raised by the siblings accessor system
    """
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return repr(self.message)

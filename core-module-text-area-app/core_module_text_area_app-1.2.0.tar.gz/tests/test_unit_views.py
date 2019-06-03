""" Module Text Area testing
"""
from unittest.case import TestCase

from django.http.request import HttpRequest

from core_module_text_area_app.views.views import TextAreaModule
from xml_utils.xsd_tree.operations.xml_entities import XmlEntities



class TestTextAreaModuleRetrieveData(TestCase):

    def test_text_area_module_retrieve_data_returns_element_if_data_given(self):
        # Arrange
        request = HttpRequest()
        data = 'dummy text'
        request.method = 'GET'
        request.GET = {
            'data': data,
        }
        my_module = TextAreaModule()
        # Act
        result = my_module._retrieve_data(request)
        self.assertEqual(True, result == data)

    def test_text_area_module_retrieve_data_returns_empty_if_no_data_given(self):
        # Arrange
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {
        }
        my_module = TextAreaModule()
        # Act
        result = my_module._retrieve_data(request)
        self.assertEqual(True, result == '')

    def test_text_area_module_retrieve_data_returns_element_if_selected_data_given(self):
        # Arrange
        request = HttpRequest()
        label = 'descritpion'
        data = 'dummy text'
        request.method = 'POST'
        request.POST = {
            'label': label,
            'data': data,
        }
        my_module = TextAreaModule()
        # Act
        result = my_module._retrieve_data(request)
        self.assertEqual(True, result == data)

    def test_text_area_module_retrieve_data_returns_empty_if_no_selected_data_given(self):
        # Arrange
        request = HttpRequest()
        request.method = 'POST'
        request.POST = {
        }
        my_module = TextAreaModule()
        # Act
        result = my_module._retrieve_data(request)
        self.assertEqual(True, result == '')


class TestTextAreaModuleRenderData(TestCase):

    def test_text_area_module_render_data_returns_always_empty(self):
        # Arrange
        request = HttpRequest()
        data = 'dummy text'
        my_module = TextAreaModule()
        my_module.data_xml_entities = XmlEntities()
        my_module.data = data
        # Act
        result = my_module._render_data(request)
        self.assertEqual(True, result == '')

import os
import unittest
import json

from pyramid.compat import text_
from pyramid.testing import DummyRequest

from tests import (
    get_LocatieElement_object,
    get_Perceel_object,
    get_LocatieAdres_object,
    get_OpenbaarDomein_object,
)
from oe_geoutils.renderer import (
    locatie_element_adapter,
    locatie_adres_adapter,
    perceel_adapter,
    openbaar_domein_adapter
)

TEST_DIR = os.path.dirname(__file__)

with open(os.path.join(TEST_DIR, 'fixtures/locaties.json'), 'rb') as f:
    locaties_json = json.loads(text_(f.read()))


class RendererTests(unittest.TestCase):

    def setUp(self):
        self.request = DummyRequest()

    def test_locatie_element_adapter(self):
        obj = get_LocatieElement_object()
        element_json = locatie_element_adapter(obj, self.request)
        element = [el for el in locaties_json['locatie']['elementen'] if el['id'] == 4][0]
        self.assertDictEqual(element_json, element)


    def test_locatie_adres_adapter(self):
        self.maxDiff = None
        obj = get_LocatieAdres_object()
        element_json = locatie_adres_adapter(obj, self.request)
        element = [el for el in locaties_json['locatie']['elementen'] if el['id'] == 2][0]
        self.assertDictEqual(element_json, element)


    def test_perceel_adapter(self):
        obj = get_Perceel_object()
        element_json = perceel_adapter(obj, self.request)
        element = [el for el in locaties_json['locatie']['elementen'] if el['id'] == 1][0]
        self.assertDictEqual(element_json, element)


    def test_openbaar_domein_adapter(self):
        obj = get_OpenbaarDomein_object()
        element_json = openbaar_domein_adapter(obj, self.request)
        element = [el for el in locaties_json['locatie']['elementen'] if el['id'] == 3][0]
        self.assertDictEqual(element_json, element)

import os
import unittest
import json

from pyramid.compat import text_
from pyramid.testing import DummyModel

from oe_geoutils.data.mappers import (
    _map_locatie,
    _map_locatie_elementen,
)

TEST_DIR = os.path.dirname(__file__)

with open(os.path.join(TEST_DIR, 'fixtures/locaties.json'), 'rb') as f:
    locaties_json = json.loads(text_(f.read()))


class MappersTests(unittest.TestCase):

    def setUp(self):
        self.model = DummyModel()

    def test_map_locatie(self):
        self.model = _map_locatie(locaties_json['locatie'], self.model)
        self.assertIsNotNone(self.model.contour)
        self.assertIsInstance(self.model.locatie_elementen, list)
        self.assertEqual(len(self.model.locatie_elementen), 4)

    def test_map_locatie_elementen(self):
        locatie_elementen = _map_locatie_elementen(locaties_json['locatie']['elementen'])
        self.assertIsInstance(locatie_elementen, list)
        self.assertEqual(len(locatie_elementen), 4)
        # Perceel
        obj = [el for el in locatie_elementen
               if el.type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel'][0]
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel')
        self.assertEqual(obj.provincie_niscode, 20001)
        self.assertEqual(obj.provincie_naam, 'Vlaams-Brabant')
        self.assertEqual(obj.gemeente_niscode, 24062)
        self.assertEqual(obj.gemeente_naam, 'Leuven')
        self.assertEqual(obj.gemeente_crab_id, 143)
        self.assertEqual(obj.afdeling, 'LEUVEN  5 AFD')
        self.assertEqual(obj.sectie, 'F')
        self.assertEqual(obj.perceel, '0415/00F000')
        self.assertEqual(obj.capakey, '24505F0415/00F000')
        # Openbaar Domein
        obj = [el for el in locatie_elementen
               if el.type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein'][0]
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein')
        self.assertEqual(obj.provincie_niscode, 20001)
        self.assertEqual(obj.provincie_naam, 'Vlaams-Brabant')
        self.assertEqual(obj.gemeente_niscode, 24062)
        self.assertEqual(obj.gemeente_naam, 'Leuven')
        self.assertEqual(obj.gemeente_crab_id, 143)
        self.assertEqual(obj.omschrijving, 'Universiteitsbibliotheek Leuven')
        # LocatieAdres
        obj = [el for el in locatie_elementen
               if el.type == 'https://id.erfgoed.net/vocab/ontology#LocatieElementAdres'][0]
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElementAdres')
        self.assertEqual(obj.provincie_niscode, 20001)
        self.assertEqual(obj.provincie_naam, 'Vlaams-Brabant')
        self.assertEqual(obj.gemeente_niscode, 24062)
        self.assertEqual(obj.gemeente_naam, 'Leuven')
        self.assertEqual(obj.gemeente_crab_id, 143)
        self.assertEqual(obj.straat_id, 34819)
        self.assertEqual(obj.straat, 'Fonteinstraat')
        self.assertEqual(obj.huisnummer_id, 201984)
        self.assertEqual(obj.huisnummer, '75')
        self.assertEqual(obj.subadres_id, 2)
        self.assertEqual(obj.subadres, 'test2')
        self.assertEqual(obj.postcode, '3000')
        self.assertEqual(obj.land, 'BE')
        # LocatieElement
        obj = [el for el in locatie_elementen
               if el.type == 'https://id.erfgoed.net/vocab/ontology#LocatieElement'][0]
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElement')
        self.assertEqual(obj.provincie_niscode, 20001)
        self.assertEqual(obj.provincie_naam, 'Vlaams-Brabant')
        self.assertEqual(obj.gemeente_niscode, 24062)
        self.assertEqual(obj.gemeente_naam, 'Leuven')
        self.assertEqual(obj.gemeente_crab_id, 143)
        self.assertEqual(obj.deelgemeente_niscode, "24086X")
        self.assertEqual(obj.deelgemeente_naam, 'Oud-Heverlee')

import unittest

from tests import (
    get_LocatieElement_object,
    get_Perceel_object,
    get_LocatieAdres_object,
    get_OpenbaarDomein_object,
)
from oe_geoutils.data.models import (
    LocatieElement,
    LocatieAdres,
    Perceel,
    OpenbaarDomein,
)


class ModelTests(unittest.TestCase):

    def test_locatie_element(self):
        obj = get_LocatieElement_object()
        self.assertIsInstance(obj, LocatieElement)
        self.assertEqual(obj.id, 4)
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElement')
        self.assertEqual(obj.resource_object_id, 9999)
        self.assertEqual(obj.provincie_niscode, 20001)
        self.assertEqual(obj.provincie_naam, 'Vlaams-Brabant')
        self.assertEqual(obj.gemeente_niscode, 24062)
        self.assertEqual(obj.gemeente_naam, 'Leuven')
        self.assertEqual(obj.gemeente_crab_id, 143)

    def test_locatie_adres(self):
        obj = get_LocatieAdres_object()
        self.assertIsInstance(obj, LocatieAdres)
        self.assertEqual(obj.id, 2)
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElementAdres')
        self.assertEqual(obj.resource_object_id, 9999)
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

    def test_perceel(self):
        obj = get_Perceel_object()
        self.assertIsInstance(obj, Perceel)
        self.assertEqual(obj.id, 1)
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElementPerceel')
        self.assertEqual(obj.resource_object_id, 9999)
        self.assertEqual(obj.provincie_niscode, 20001)
        self.assertEqual(obj.provincie_naam, 'Vlaams-Brabant')
        self.assertEqual(obj.gemeente_niscode, 24062)
        self.assertEqual(obj.gemeente_naam, 'Leuven')
        self.assertEqual(obj.gemeente_crab_id, 143)
        self.assertEqual(obj.afdeling, 'LEUVEN  5 AFD')
        self.assertEqual(obj.sectie, 'F')
        self.assertEqual(obj.perceel, '0415/00F000')
        self.assertEqual(obj.capakey, '24505F0415/00F000')

    def test_openbaar_domein(self):
        obj = get_OpenbaarDomein_object()
        self.assertIsInstance(obj, OpenbaarDomein)
        self.assertEqual(obj.id, 3)
        self.assertEqual(obj.type, 'https://id.erfgoed.net/vocab/ontology#LocatieElementOpenbaarDomein')
        self.assertEqual(obj.resource_object_id, 9999)
        self.assertEqual(obj.provincie_niscode, 20001)
        self.assertEqual(obj.provincie_naam, 'Vlaams-Brabant')
        self.assertEqual(obj.gemeente_niscode, 24062)
        self.assertEqual(obj.gemeente_naam, 'Leuven')
        self.assertEqual(obj.gemeente_crab_id, 143)
        self.assertEqual(obj.omschrijving, 'Universiteitsbibliotheek Leuven')

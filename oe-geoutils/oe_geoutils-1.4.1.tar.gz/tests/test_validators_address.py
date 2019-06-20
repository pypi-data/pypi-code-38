# -*- coding: utf-8 -*-
from tests import crab_gateway_mock

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
import unittest

import colander
from oe_geoutils.validation.validators_address import CrabAdresSchemaNode
from pyramid import testing

import pytest
from crabpy.gateway.crab import CrabGateway
from crabpy.client import crab_factory


integration = pytest.mark.skipif(
    not pytest.config.getoption("--integration"),
    reason="need --integration option to run"
)


class AdressenSchemaTests(unittest.TestCase):
    def setUp(self):
        request = testing.DummyRequest()
        request.crab_gateway = Mock(return_value=crab_gateway_mock)

        adressen_schema = CrabAdresSchemaNode()

        self.schema = adressen_schema.bind(
            request=request
        )

    def tearDown(self):
        del self.schema

    def test_adres_None(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": None,
                "gemeente_id": None,
            }
        )
        self.assertIsNone(res)

    def test_adres_None_2(self):
        res = self.schema.deserialize(
            {
            }
        )
        self.assertIsNone(res)

    def test_adres_gemeente_id_from_gemeente_val(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": None,
            }
        )
        self.assertEqual(191, res["gemeente_id"])

    def test_adres_validatie(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraatje",
                "straat_id": 48086,
                "huisnummer": "68",
                "huisnummer_id": 270059,
                "subadres": "A",
                "subadres_id": 1441952
            }
        )
        self.assertEqual("Nieuwstraat", res['straat'])
        self.assertEqual("6", res['huisnummer'])
        self.assertEqual("1", res['subadres'])

    def test_adres_validatie_var(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraatje",
                "straat_id": 48086,
                "huisnummer": "6",
                "huisnummer_id": None,
                "subadres": "1",
                "subadres_id": None
            }
        )
        self.assertEqual("Nieuwstraat", res['straat'])
        self.assertEqual(270059, res['huisnummer_id'])
        self.assertEqual(1441952, res['subadres_id'])

    def test_adres_geen_crab(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "BE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraat",
                "straat_id": None,
                "huisnummer": "6",
                "huisnummer_id": None,
                "subadres": "1",
                "subadres_id": None
            }
        )
        self.assertEqual(48086, res['straat_id'])
        self.assertEqual(270059, res['huisnummer_id'])
        self.assertEqual(1441952, res['subadres_id'])

    def test_adres_validatie_non_be(self):
        res = self.schema.deserialize(
            {
                "id": 1,
                "land": "DE",
                "postcode": "8300",
                "gemeente": "Knokke-Heist",
                "gemeente_id": 191,
                "straat": "Nieuwstraatje",
                "straat_id": 48086,
                "huisnummer": "68",
                "huisnummer_id": 887821,
                "subadres_id": 566
            }
        )
        self.assertIsNone(res["gemeente_id"])
        self.assertIsNone(res["huisnummer_id"])
        self.assertIsNone(res["straat_id"])
        self.assertIsNone(res["subadres_id"])

    def test_straat_niet_in_gemeente(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "2500",
                    "gemeente": "Lier",
                    "gemeente_id": 36,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('de straat Nieuwstraat met id 48086 ligt niet in gemeente Lier', inv.exception.asdict()[''])

    def test_huisnummer_niet_in_straat(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "2500",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "69",
                    "huisnummer_id": 882821
                }
            )
        self.assertEqual('het huisnummer 69 met id 882821 ligt niet in straat Nieuwstraat', inv.exception.asdict()[''])

    def test_huisnummer_id_zonder_straat_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "2500",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraattrhyj",
                    "straat_id": None,
                    "huisnummer": "68",
                    "huisnummer_id": 882821
                }
            )
        self.assertEqual('als er een huisnummer_id wordt gegeven, moet men ook het straat_id invullen',
                         inv.exception.asdict()[''])

    def test_postcode(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "1025",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('postcode 1025 is niet correct voor dit adres, mogelijke postcode is 8300',
                         inv.exception.asdict()[''])

    def test_postcode_geen_huisnummer(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "1025",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086
                }
            )
        self.assertEqual("postcode 1025 is niet correct voor dit adres, mogelijke postcode(s) zijn ['8300', '8301']",
                         inv.exception.asdict()[''])

    def test_ongeldige_gemeente_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191023,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('ongeldig gemeente_id 191023',
                         inv.exception.asdict()[''])

    def test_ongeldige_gemeente(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Test",
                    "gemeente_id": None,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('geen correcte gemeente_id gevonden voor de gemeente Test',
                         inv.exception.asdict()[''])

    def test_ongeldige_straat_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 480865567624,
                    "huisnummer": "68",
                    "huisnummer_id": 887821
                }
            )
        self.assertEqual('ongeldig straat_id',
                         inv.exception.asdict()[''])

    def test_ongeldige_huisnummer_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "68",
                    "huisnummer_id": 887821125895
                }
            )
        self.assertEqual('ongeldig huisnummer_id',
                         inv.exception.asdict()[''])

    def test_ongeldige_subadres_id(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "6",
                    "huisnummer_id": 270059,
                    "subadres": "1",
                    "subadres_id": 4556789912335445
                }
            )
        self.assertEqual('ongeldig subadres_id',
                         inv.exception.asdict()[''])

    def test_subadres_id_not_at_huisnummer(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "id": 1,
                    "land": "BE",
                    "postcode": "8300",
                    "gemeente": "Knokke-Heist",
                    "gemeente_id": 191,
                    "straat": "Nieuwstraat",
                    "straat_id": 48086,
                    "huisnummer": "6",
                    "huisnummer_id": 270059,
                    "subadres": "11",
                    "subadres_id": 1442188
                }
            )
        self.assertEqual('het subadres 11 met id 1442188 ligt niet op huisnummer 6',
                         inv.exception.asdict()[''])

    def test_geen_gemeente_id_buitenland(self):
        res = self.schema.deserialize(
            {
                "land": "DE",
                "gemeente": u"Köln",
                "adrestype": {
                    "id": 1
                }
            }
        )
        self.assertEqual(u"Köln", res['gemeente'])

    def test_buitenland(self):
        res = self.schema.deserialize(
            {
                "land": "DE",
                "gemeente": u"Köln",
                "adrestype": {
                    "id": 1
                }
            }
        )
        self.assertEqual(u"Köln", res['gemeente'])

    def test_ongeldig_land(self):
        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(
                {
                    "land": "XX",
                    "gemeente": u"Köln",
                    "adrestype": {
                        "id": 1
                    }
                }
            )
        self.assertEqual("ongeldige landcode XX, dit is geen ISO 3166 code",
                         inv.exception.asdict()[''])

    def test_CrabAdresSchemaNode_handles_missing(self):
        class ParentSchema(colander.MappingSchema):
            child_schema = CrabAdresSchemaNode(missing=colander.required)
            some_node = colander.SchemaNode(colander.String(), missing='some value')

        json_data = {'some_node': 'some other value'}
        schema = ParentSchema()
        with self.assertRaises(colander.Invalid) as ex:
            schema.deserialize(json_data)

    def test_CrabAdresSchemaNode_handles_missing_default(self):
        class ParentSchema(colander.MappingSchema):
            child_schema = CrabAdresSchemaNode(missing=None)
            some_node = colander.SchemaNode(colander.String(), missing='some value')

        json_data = {'some_node': 'some other value'}
        schema = ParentSchema()
        deserialized = schema.deserialize(json_data)
        self.assertIsNotNone(deserialized)
        self.assertIn('some_node', deserialized)
        self.assertIn('child_schema', deserialized)
        self.assertEqual(deserialized['child_schema'], None)

    def test_no_postal_code(self):
        adres = {
            "land": "BE",
            "gemeente": "Antwerpen",
            "straat": "Bist",
            "huisnummer": "40"
        }

        res = self.schema.deserialize(adres)
        self.assertIsNotNone(res['straat'])
        self.assertIsNotNone(res['straat_id'])
        self.assertIsNotNone(res['huisnummer'])
        self.assertIsNotNone(res['huisnummer_id'])
        self.assertIsNone(res['postcode'])

    def test_same_address_different_postal_code(self):
        adres = {
            "land": "BE",
            "gemeente": "Antwerpen",
            "straat": "Bist",
            "huisnummer": "40",
            "postcode": "2180"
        }
        res_2180 = self.schema.deserialize(adres)
        adres['postcode'] = "2610"
        res_2610 = self.schema.deserialize(adres)

        self.assertIsNotNone(res_2180['straat'])
        self.assertIsNotNone(res_2610['straat'])
        self.assertIsNotNone(res_2180['straat_id'])
        self.assertIsNotNone(res_2610['straat_id'])
        self.assertIsNotNone(res_2180['huisnummer'])
        self.assertIsNotNone(res_2610['huisnummer'])
        self.assertIsNotNone(res_2180['huisnummer_id'])
        self.assertIsNotNone(res_2610['huisnummer_id'])

        self.assertEqual(res_2180['straat'], res_2610['straat'])
        self.assertEqual(res_2180['huisnummer'], res_2610['huisnummer'])

        self.assertNotEqual(res_2180['straat_id'], res_2610['straat_id'])
        self.assertNotEqual(res_2180['huisnummer_id'], res_2610['huisnummer_id'])

    def test_same_address_wrong_postal_code(self):
        adres = {
            "land": "BE",
            "gemeente": "Antwerpen",
            "straat": "Bist",
            "huisnummer": "40",
            "postcode": "7180"
        }

        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(adres)
        self.assertIn("postcode 7180 is niet correct voor dit adres",
                      inv.exception.asdict()[''])


@integration
class AdressenSchemaTestsIntegration(unittest.TestCase):

    def setUp(self):
        request = testing.DummyRequest()
        self.crab_client = crab_factory()
        self.crab_gateway = CrabGateway(
            self.crab_client
        )
        request.crab_gateway = Mock(return_value=self.crab_gateway)
        adressen_schema = CrabAdresSchemaNode()
        self.schema = adressen_schema.bind(
            request=request
        )

    def tearDown(self):
        self.crab_client = None
        self.crab = None
        del self.schema

    def test_no_postal_code(self):
        adres = {
            "land": "BE",
            "gemeente": "Antwerpen",
            "straat": "Bist",
            "huisnummer": "40"
        }

        res = self.schema.deserialize(adres)
        self.assertIsNotNone(res['straat'])
        self.assertIsNotNone(res['straat_id'])
        self.assertIsNotNone(res['huisnummer'])
        self.assertIsNotNone(res['huisnummer_id'])
        self.assertIsNone(res['postcode'])

    def test_same_address_different_postal_code(self):
        adres = {
            "land": "BE",
            "gemeente": "Antwerpen",
            "straat": "Bist",
            "huisnummer": "40",
            "postcode": "2180"
        }
        res_2180 = self.schema.deserialize(adres)
        adres['postcode'] = "2610"
        print(res_2180)
        res_2610 = self.schema.deserialize(adres)
        print(res_2610)

        self.assertIsNotNone(res_2180['straat'])
        self.assertIsNotNone(res_2610['straat'])
        self.assertIsNotNone(res_2180['straat_id'])
        self.assertIsNotNone(res_2610['straat_id'])
        self.assertIsNotNone(res_2180['huisnummer'])
        self.assertIsNotNone(res_2610['huisnummer'])
        self.assertIsNotNone(res_2180['huisnummer_id'])
        self.assertIsNotNone(res_2610['huisnummer_id'])

        self.assertEqual(res_2180['straat'], res_2610['straat'])
        self.assertEqual(res_2180['huisnummer'], res_2610['huisnummer'])

        self.assertNotEqual(res_2180['straat_id'], res_2610['straat_id'])
        self.assertNotEqual(res_2180['huisnummer_id'], res_2610['huisnummer_id'])

    def test_same_address_wrong_postal_code(self):
        adres = {
            "land": "BE",
            "gemeente": "Antwerpen",
            "straat": "Bist",
            "huisnummer": "40",
            "postcode": "7180"
        }

        with self.assertRaises(colander.Invalid) as inv:
            self.schema.deserialize(adres)
        self.assertIn("postcode 7180 is niet correct voor dit adres",
                      inv.exception.asdict()[''])

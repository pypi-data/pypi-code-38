# -*- coding: utf-8 -*-
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # pragma: no cover
from crabpy.gateway.exception import GatewayRuntimeException
import colander
from pyramid import testing
import unittest
from oe_geoutils.validation.validators_cadaster_parcels import CadasterSchemaNode


class Afdeling(object):
    def __init__(self):
        self.naam = "LEUVEN  5 AFD"


class Sectie(object):
    def __init__(self):
        self.id = "F"
        self.afdeling = Afdeling()


class Perceel(object):
    def __init__(self):
        self.sectie = Sectie()
        self.id = "0415/00F000"


def get_perceel_by_capakey(capakey):
    if capakey == 'invalid':
        raise AttributeError
    return Perceel()


capakey_gateway_mock = Mock()
capakey_gateway_mock.get_perceel_by_capakey = get_perceel_by_capakey


class CadasterParcelSchemaTests(unittest.TestCase):
    def setUp(self):
        request = testing.DummyRequest()
        request.capakey_gateway = Mock(return_value=capakey_gateway_mock)

        cadaster_schema = CadasterSchemaNode()

        self.schema = cadaster_schema.bind(
            request=request
        )

    def tearDown(self):
        del self.schema

    def test_capakey(self):
        res = self.schema.deserialize(
            {
                "afdeling": u"LEUVEN  5 AFD",
                "capakey": u"24505F0415/00F000"
            }
        )
        self.assertEqual({"afdeling": "LEUVEN  5 AFD", "perceel": None, "sectie": None,
                          "capakey": "24505F0415/00F000"}, res)

    def test_exception(self):
        self.assertRaises(colander.Invalid, self.schema.deserialize, {"capakey": u"invalid"})

    def test_CadasterSchemaNode_handles_missing(self):
        class ParentSchema(colander.MappingSchema):
            child_schema = CadasterSchemaNode(missing=colander.required)
            some_node = colander.SchemaNode(colander.String(), missing='some value')

        json_data = {'some_node': 'some other value'}
        schema = ParentSchema()
        with self.assertRaises(colander.Invalid) as ex:
            schema.deserialize(json_data)

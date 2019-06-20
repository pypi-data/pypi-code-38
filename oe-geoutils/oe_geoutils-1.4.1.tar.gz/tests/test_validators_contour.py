import unittest
from pyramid import testing
import colander
from oe_geoutils.validation.validators_contour import GeometrieSchemaNode, PointGeometrieSchemaNode, GeometryValidator,\
    GeoJson, MultiPointGeometrieSchemaNode

import collections

Node = collections.namedtuple('Node', ['name'])


class GeoJsonTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.max_area = 5

        self.geometrie = GeometrieSchemaNode(max_area=5)

        self.geojson_valid = {
            "type": "MultiPolygon",
            "coordinates": [[[[152184.01399999947, 212331.8648750011], [152185.94512499947, 212318.6137500011],
                              [152186.13837499946, 212318.6326250011], [152186.86699999947, 212313.9570000011],
                              [152186.91462499945, 212313.65187500112], [152192.45099999948, 212314.2943750011],
                              [152190.69212499948, 212319.2656250011], [152199.58799999946, 212319.5248750011],
                              [152197.85312499947, 212327.9388750011], [152197.57199999946, 212327.8978750011],
                              [152197.08099999945, 212333.2668750011], [152184.01399999947, 212331.8648750011]]]],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        }
        self.geojson_invalid_type = {
            "type": "InvalidType",
            "coordinates": [
                [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
                [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
                 [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]
            ],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        }
        self.geojson_geom_not_in_flanders = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
                [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
                 [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]
            ],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        }
        self.geojson_point = {
            "type": "Point",
            "coordinates": [102.0, 2.0],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        }
        self.geojson_srid_4326 = {
            "type": "MultiPolygon",
            "coordinates": [[[[152184.01399999947, 212331.8648750011], [152185.94512499947, 212318.6137500011],
                              [152186.13837499946, 212318.6326250011], [152186.86699999947, 212313.9570000011],
                              [152186.91462499945, 212313.65187500112], [152192.45099999948, 212314.2943750011],
                              [152190.69212499948, 212319.2656250011], [152199.58799999946, 212319.5248750011],
                              [152197.85312499947, 212327.9388750011], [152197.57199999946, 212327.8978750011],
                              [152197.08099999945, 212333.2668750011], [152184.01399999947, 212331.8648750011]]]],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::4326"
                }
            }
        }
        self.geojson_invalid_geom = {
            "type": "MultiPolygon",
            "coordinates": [[[[152184.01399999947, 212331.8648750011],[152184.01399999947, 212331.8648750010],
                              [152184.01399999947, 212331.8648750010]]]],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        }
        self.geojson_invalid_type_no_crs = {
            "type": "MultiPolygon",
            "coordinates": [[[[152184.01399999947, 212331.8648750011], [152185.94512499947, 212318.6137500011],
                              [152186.13837499946, 212318.6326250011], [152186.86699999947, 212313.9570000011],
                              [152186.91462499945, 212313.65187500112], [152192.45099999948, 212314.2943750011],
                              [152190.69212499948, 212319.2656250011], [152199.58799999946, 212319.5248750011],
                              [152197.85312499947, 212327.9388750011], [152197.57199999946, 212327.8978750011],
                              [152197.08099999945, 212333.2668750011], [152184.01399999947, 212331.8648750010]]]],
        }
        self.geojson_intersecting_geom = {
            "type": "MultiPolygon",
            "coordinates": [[[[136311.36331804123, 189479.80567278434], [136330.70361803696, 189482.001472787],
                              [136330.25991803684, 189485.51207278483], [136312.9926180562, 189622.26197274867],
                              [136309.1386180551, 189621.94727274682], [136287.7971180621, 189620.205472745],
                              [136299.8650180514, 189546.03157276567], [136303.254718051, 189525.19737276994],
                              [136303.72911804935, 189522.28157277592], [136303.86311804503, 189521.45807277132],
                              [136304.32241804857, 189518.63487277366], [136305.1149180444, 189513.7637727782],
                              [136305.38571804608, 189512.09917277843], [136310.10041803963, 189483.12087278347],
                              [136310.65291804122, 189479.72507278528], [136311.36331804123, 189479.80567278434]]],
                            [[[136337.15461803263, 189483.00437278394], [136336.6959180319, 189486.44747278653],
                              [136328.27671804628, 189549.64527276624], [136390.48041802715, 189555.04837277252],
                              [136380.7150180388, 189628.1505727535], [136349.4110180502, 189625.37497274857],
                              [136329.42661805183, 189623.6030727476], [136312.9926180562, 189622.26197274867],
                              [136330.25991803684, 189485.51207278483], [136330.70361803696, 189482.001472787],
                              [136337.15461803263, 189483.00437278394]]]],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        }
        self.geojson_very_large = {
            "type": "MultiPolygon",
            "coordinates": [[[
                [149287.72860779167967848, 218916.39169927779585123],
                [153788.90851591509999707, 182097.94758232310414314],
                [220400.85877580623491667, 180574.3110011201351881],
                [220400.85877580623491667, 180574.3110011201351881],
                [149287.72860779167967848, 218916.39169927779585123]
            ]]],
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:EPSG::31370"
                }
            }
        }

    def tearDown(self):
        testing.tearDown()

    def test_valid_max_area(self):
        geomschemanode = GeometrieSchemaNode(max_area="4")
        self.assertEqual(40000, geomschemanode.max_area)
        geomschemanode = GeometrieSchemaNode(max_area=5.2)
        self.assertEqual(52000, geomschemanode.max_area)

    def test_invalid_max_area(self):
        geomschemanode = GeometrieSchemaNode(max_area="test")
        self.assertEqual(80000000, geomschemanode.max_area)

    def test_validGeoJson(self):
        validated = self.geometrie.deserialize(self.geojson_valid)
        self.assertIsInstance(validated, dict)

    def test_geojson_serialize(self):
        self.assertRaises(NotImplementedError, GeoJson().serialize, None, None)

    def test_geojson_serializes_none(self):
        self.assertIsNone(GeoJson().build_shape(None))
        self.assertEqual(colander.null, GeoJson().deserialize(None, {}))
        self.assertEqual(colander.null, GeoJson().deserialize(None, None))

    def test_geojson_invalid_type(self):
        self.assertRaises(
            colander.Invalid,
            self.geometrie.deserialize, self.geojson_invalid_type)

    def test_geometrie_validator_none(self):
        self.assertRaises(
            colander.Invalid, GeometryValidator, None, {})
        self.assertRaises(
            colander.Invalid, GeometryValidator, None, None)

    def test_geometrie_validator_no_multipolygon(self):
        self.assertRaises(
            colander.Invalid, GeometryValidator(None, self.geojson_point).validate_multipolygon, self.max_area)

    def test_geometrie_validator_invalid_srid(self):
        self.assertRaises(
            colander.Invalid, GeometryValidator(None, self.geojson_srid_4326).validate_multipolygon, self.max_area)

    def test_geometrie_validator_invalid_geometry(self):
        self.assertRaises(
            colander.Invalid, GeometryValidator(None, self.geojson_invalid_geom).validate_multipolygon, self.max_area)

    def test_geometrie_validator_geometry_not_in_flanders(self):
        self.assertRaises(
            colander.Invalid, GeometryValidator(None, self.geojson_geom_not_in_flanders).validate_multipolygon,
            self.max_area)

    def test_geometrie_validator_invalid_geojson(self):
        self.assertRaises(
            colander.Invalid, GeometryValidator, None, self.geojson_invalid_type)

    def test_geometrie_validator_invalid_geojson_no_crs(self):
        self.assertRaises(
            colander.Invalid, GeometryValidator(None, self.geojson_invalid_type_no_crs).validate_multipolygon,
            self.max_area)

    def test_geometrie_validator_intersecting_geometry(self):
        self.assertRaises(
            colander.Invalid, self.geometrie.deserialize,
                {"type": "Polygon", "coordinates": [[[0, 0], [0, 0], [0, 0], [0, 0]]],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}})

    def test_geometrie_validator_empty_geometry(self):
        self.geometrie.deserialize(self.geojson_intersecting_geom)

    def test_geometrie_validator_very_large(self):
        self.assertRaises(
            colander.Invalid, self.geometrie.deserialize, self.geojson_very_large)

    def test_schema_node_with_none(self):
        self.assertRaises(colander.Invalid, self.geometrie.deserialize, None)

    def test_schema_node_with_max_area_kwarg(self):
        schema_node = GeometrieSchemaNode(max_area=6)
        self.assertEqual(6 * 10000, schema_node.max_area)

    def test_schema_node_with_max_area_arg(self):
        schema_node = GeometrieSchemaNode(6)
        self.assertEqual(6 * 10000, schema_node.max_area)

    def test_schema_node_default_missing(self):
        result = GeometrieSchemaNode(max_area=5, missing=None).deserialize(None)
        self.assertIsNone(result)

    def test_point_schema_node_default_missing(self):
        result = PointGeometrieSchemaNode(missing=None).deserialize(None)
        self.assertIsNone(result)

    def test_multipoint_schema_node_default_missing(self):
        result = MultiPointGeometrieSchemaNode(missing=None).deserialize(None)
        self.assertIsNone(result)

    def test_node_missing_in_schema(self):
        class TestClass(colander.MappingSchema):
            some = colander.SchemaNode(colander.String())
            geometry = GeometrieSchemaNode(max_area=1000, missing=None)

        test_instance = TestClass().deserialize({'some': 'thing'})
        self.assertEqual('thing', test_instance['some'])
        self.assertIsNone(test_instance['geometry'])

    def test_node_in_schema(self):
        class TestClass(colander.MappingSchema):
            some = colander.SchemaNode(colander.String())
            geometry = GeometrieSchemaNode(max_area=1000, missing=None)

        test_instance = TestClass().deserialize({'some': 'thing', 'geometry': self.geojson_valid})
        self.assertEqual('thing', test_instance['some'])
        self.assertIsNotNone(test_instance['geometry'])
        self.assertIsInstance(test_instance['geometry'], dict)

    def test_node_invalid_in_schema(self):
        class TestClass(colander.MappingSchema):
            some = colander.SchemaNode(colander.String())
            geometry = GeometrieSchemaNode(max_area=1000, missing=None)
        self.assertRaises(colander.Invalid, TestClass().deserialize,
                          {'some': 'thing', 'geometry': self.geojson_invalid_geom})

    def test_point_schemanode(self):
        PointGeometrieSchemaNode().deserialize(
                {"type": "Point", "coordinates": [152185, 212318],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}})
        self.assertRaises(colander.Invalid, PointGeometrieSchemaNode().deserialize,
                {"type": "MultiPoint", "coordinates": [152185, 212318],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}})
        self.assertRaises(colander.Invalid, PointGeometrieSchemaNode().deserialize,
                {"type": "Point", "coordinates": [1521850, 2123180],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}})
        self.assertRaises(colander.Invalid, PointGeometrieSchemaNode().deserialize,
                {"type": "Point", "coordinates": [152185, 212318],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4321"}}})
        self.assertRaises(colander.Invalid, PointGeometrieSchemaNode().deserialize,
                {"type": "Point", "coordinates": [152185, 212318]})

    def test_multipoint_schemanode(self):
        MultiPointGeometrieSchemaNode().deserialize(
                {"type": "MultiPoint", "coordinates": [[152185, 212318]],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}})
        self.assertRaises(colander.Invalid, MultiPointGeometrieSchemaNode().deserialize,
                {"type": "Point", "coordinates": [152185, 212318],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}})
        self.assertRaises(colander.Invalid, MultiPointGeometrieSchemaNode().deserialize,
                {"type": "MultiPoint", "coordinates": [[1521850, 2123180]],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::31370"}}})
        self.assertRaises(colander.Invalid, MultiPointGeometrieSchemaNode().deserialize,
                {"type": "MultiPoint", "coordinates": [[152185, 212318]],
                 "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4321"}}})
        self.assertRaises(colander.Invalid, MultiPointGeometrieSchemaNode().deserialize,
                {"type": "MultiPoint", "coordinates": [[152185, 212318]]})

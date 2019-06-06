from django.contrib.gis.geos import GEOSGeometry, GeometryCollection
from snapshottest import TestCase

from .geometry_helpers import ewkt_from_feature_collection
from rescape_python_helpers import ewkt_from_feature, geometry_from_feature, geometrycollection_from_feature_collection


class GeometryHelepersTest(TestCase):
    client = None

    def test_geometry_from_feature(self):
        result = geometry_from_feature({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[49.5294835476, 2.51357303225], [51.4750237087, 2.51357303225], [51.4750237087, 6.15665815596],
                     [49.5294835476, 6.15665815596], [49.5294835476, 2.51357303225]]]
            }
        })
        assert isinstance(result, GEOSGeometry)

    def test_ewkt_from_feature(self):
        result = ewkt_from_feature({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[49.5294835476, 2.51357303225], [51.4750237087, 2.51357303225], [51.4750237087, 6.15665815596],
                     [49.5294835476, 6.15665815596], [49.5294835476, 2.51357303225]]]
            }
        })
        assert isinstance(result, str)

    def test_geometry_collection_from_feature_collection(self):
        result = geometrycollection_from_feature_collection({
            'type': 'FeatureCollection',
            'generator': 'overpass-turbo',
            'copyright': 'The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.',
            'timestamp': '2017-04-06T22:46:03Z',
            'features': [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[49.5294835476, 2.51357303225], [51.4750237087, 2.51357303225], [51.4750237087, 6.15665815596],
                         [49.5294835476, 6.15665815596], [49.5294835476, 2.51357303225]]]
                }
            },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[49.5294835476, 2.51357303225], [51.4750237087, 2.51357303225],
                             [51.4750237087, 6.15665815596],
                             [49.5294835476, 6.15665815596], [49.5294835476, 2.51357303225]]]
                    }
                }
            ]
        })
        assert isinstance(result, GeometryCollection)

    def test_ewkt_from_feature_collection(self):
        result = ewkt_from_feature_collection({
            'type': 'FeatureCollection',
            'generator': 'overpass-turbo',
            'copyright': 'The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.',
            'timestamp': '2017-04-06T22:46:03Z',
            'features': [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[49.5294835476, 2.51357303225], [51.4750237087, 2.51357303225], [51.4750237087, 6.15665815596],
                         [49.5294835476, 6.15665815596], [49.5294835476, 2.51357303225]]]
                }
            },
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[49.5294835476, 2.51357303225], [51.4750237087, 2.51357303225],
                             [51.4750237087, 6.15665815596],
                             [49.5294835476, 6.15665815596], [49.5294835476, 2.51357303225]]]
                    }
                }
            ]
        })
        assert isinstance(result, str)
import qgis # NOQA
import os
from tempfile import TemporaryDirectory
from qgis.core import QgsVectorLayer
from qgis.testing import start_app, unittest
from ..sources import GeoJSONSource
from .utils import create_layers


start_app()


class TestGeoJSONSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.id = 'planning'
        cls.url = 'https://example.com/data/planning.geojson'
        cls.layers = create_layers()

    def setUp(self):
        self.source = GeoJSONSource(self.id, self.url)

    def test_add_layer(self):
        self.source.add_layer(self.layers[0], id='station_locations')
        self.assertEqual(self.source.layer_id, 'station_locations')
        self.assertEqual(self.source.layer, self.layers[0])

        self.source.add_layer(self.layers[1])
        self.assertEqual(self.source.layer_id, self.layers[1].id())
        self.assertEqual(self.source.layer, self.layers[1])

    def test_get_layer_id(self):
        self.source.add_layer(self.layers[0], id='station_locations')
        self.assertEqual(self.source.get_layer_id(self.layers[0]), None)

    def test_get_json(self):
        json = self.source.get_json()
        self.assertEqual(json['type'], 'geojson')
        self.assertEqual(json['url'], self.url)

    def test_write(self):
        self.source.add_layer(self.layers[0], id='station_locations')

        with TemporaryDirectory() as dst_dir:
            out_path = os.path.join(dst_dir, 'output.geojson')
            self.source.write(out_path)

            layer = QgsVectorLayer(out_path, 'output', 'ogr')
            self.assertEqual(layer.featureCount(), 4)
            self.assertEqual(layer.sourceCrs().authid(), 'EPSG:4326')

            self.source.add_layer(self.layers[1], id='streets')
            self.source.write(out_path)
            layer = QgsVectorLayer(out_path, 'output', 'ogr')
            self.assertEqual(layer.featureCount(), 3)
            self.assertEqual(layer.sourceCrs().authid(), 'EPSG:4326')


if __name__ == '__main__':
    unittest.main()

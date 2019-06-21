import qgis # NOQA
import json
import os
import sqlite3
from tempfile import TemporaryDirectory
from qgis.testing import start_app, unittest
from ..sources import VectorSource
from .utils import create_layers


start_app()


class TestVectorSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.id = 'planning'
        cls.url = 'https://example.com/tiles/planning.json'
        # Use GeoJSON format for this test suite, because converting
        # GML -> GeoPackage produces an OGR error (wrong field type for fid).
        cls.layers = create_layers('geojson')

    def setUp(self):
        self.source = VectorSource(self.id, self.url)

    def _add_layers(self):
        self.source.add_layer(
            self.layers[0], id='station_locations', min_zoom=10, max_zoom=14)
        self.source.add_layer(self.layers[1])

    def test_add_layer(self):
        self._add_layers()

        station_layer, station_options = self.source.layers[0]
        self.assertEqual(station_layer, self.layers[0])
        self.assertEqual(station_options['id'], 'station_locations')
        self.assertEqual(station_options['min_zoom'], 10)
        self.assertEqual(station_options['max_zoom'], 14)

        street_layer, street_options = self.source.layers[1]
        self.assertEqual(street_layer, self.layers[1])
        self.assertEqual(street_options['id'], self.layers[1].id())
        self.assertEqual(street_options['min_zoom'], 0)
        self.assertEqual(street_options['max_zoom'], 22)

    def test_get_layer_id(self):
        self._add_layers()
        self.assertEqual(
            self.source.get_layer_id(self.layers[0]), 'station_locations')

    def test_get_json(self):
        json = self.source.get_json()
        self.assertEqual(json['type'], 'vector')
        self.assertEqual(json['url'], self.url)

    def test_write(self):
        self._add_layers()

        with TemporaryDirectory() as dst_dir:
            out_path = os.path.join(dst_dir, 'output.mbtiles')
            self.source.write(out_path)

            conn = sqlite3.connect(out_path)
            cur = conn.cursor()
            cur.execute('SELECT * FROM metadata')
            metadata = dict(cur.fetchall())
            metadata_json = json.loads(metadata['json'])
            layers = metadata_json['vector_layers']

            self.assertEqual(metadata['minzoom'], '0')
            self.assertEqual(metadata['maxzoom'], '22')
            self.assertEqual(len(layers), 2)
            self.assertEqual(layers[0]['id'], 'station_locations')
            self.assertEqual(layers[1]['id'], self.layers[1].id())

            cur.execute('SELECT count(*) FROM tiles')
            tile_count = cur.fetchone()[0]
            self.assertEqual(tile_count, 850)

            conn.close()


if __name__ == '__main__':
    unittest.main()

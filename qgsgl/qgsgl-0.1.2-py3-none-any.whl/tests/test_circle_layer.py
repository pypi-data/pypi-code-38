from ..layer import CircleLayer
from qgis.testing import start_app, unittest
from .utils import create_layers, set_single_symbol

start_app()


class TestLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layers = set_single_symbol(create_layers())

    def setUp(self):
        self.circle_layer = CircleLayer(
                        self.layers[0].renderer().symbol().symbolLayers()[0])

    def test_circle_layer(self):
        self.assertEqual(self.circle_layer.get_type(), 'circle')
        self.assertEqual(
            self.circle_layer.get_paint_properties()['circle-color'],
            'rgba(0, 225, 0, 1.0)')
        self.circle_layer.qgis_symbol_layer.setSize(2)
        self.assertEqual(
            self.circle_layer.get_paint_properties(
                output_dpi=96)['circle-radius'],
            3.7795275590551185)


if __name__ == '__main__':
    unittest.main()

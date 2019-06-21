from ..layer import FillLayer
from qgis.testing import start_app, unittest
from .utils import create_layers, set_single_symbol

start_app()


class TestLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layers = set_single_symbol(create_layers())

    def setUp(self):
        self.fill_layer = FillLayer(
                        self.layers[2].renderer().symbol().symbolLayers()[0])

    def test_fill_layer(self):
        self.assertEqual(self.fill_layer.get_type(), 'fill')

        res = self.fill_layer.get_paint_properties()
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['fill-color'], 'rgba(0, 225, 0, 1.0)')


if __name__ == '__main__':
    unittest.main()

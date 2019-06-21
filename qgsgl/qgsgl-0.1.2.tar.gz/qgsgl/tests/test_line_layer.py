from ..layer import LineLayer
from qgis.testing import start_app, unittest
from .utils import create_layers, set_single_symbol

start_app()


class TestLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layers = set_single_symbol(create_layers())

    def setUp(self):
        self.line_layer = LineLayer(
                        self.layers[1].renderer().symbol().symbolLayers()[0])
        self.fill_layer = LineLayer(
                        self.layers[2].renderer().symbol().symbolLayers()[0])

    def test_line_layer(self):
        self.assertEqual(self.line_layer.get_type(), 'line')

        res = self.line_layer.get_paint_properties(96)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['line-color'], 'rgba(0, 225, 0, 1.0)')
        self.assertEqual(res['line-width'], 0.9826771653543308)

    def test_fill_border_layer(self):
        self.assertEqual(self.fill_layer.get_type(), 'line')
        res = self.fill_layer.get_paint_properties(96)
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['line-color'], 'rgba(35, 35, 35, 1.0)')
        self.assertEqual(res['line-width'], 0.9826771653543308)


if __name__ == '__main__':
    unittest.main()

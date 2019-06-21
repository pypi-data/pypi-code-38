from ..legend import Legend, LegendItem
from qgis.testing import start_app, unittest
from .utils import create_layers, set_single_symbol


start_app()


class TestLegend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legend = Legend()
        cls.layers = set_single_symbol(create_layers())

    def setUp(self):
        self.legend_items_1 = LegendItem(self.layers[0].renderer().symbol(),
                                         'symbol_1')
        self.legend_items_2 = LegendItem(self.layers[1].renderer().symbol(),
                                         'symbol_2')
        self.legend_items_3 = LegendItem(self.layers[2].renderer().symbol(),
                                         'symbol_3')
        self.legend.add_item(self.legend_items_1)
        self.legend.add_item(self.legend_items_2)
        self.legend.add_item(self.legend_items_3)

    def test_legend_creation(self):
        self.assertTrue(isinstance(self.legend, Legend))

    def test_add_symbol(self):
        self.assertEqual(len(self.legend.legend_items), 3)


if __name__ == '__main__':
    unittest.main()

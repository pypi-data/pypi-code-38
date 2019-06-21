from ..legend import LegendItem
from qgis.testing import start_app, unittest
from .utils import create_layers, set_single_symbol


start_app()


class TestLegendItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layers = set_single_symbol(create_layers())
        cls.legend_items = LegendItem(cls.layers[0].renderer().symbol(),
                                      'name')

    def setUp(self):
        pass

    def test_legen_creation(self):
        self.assertTrue(isinstance(self.legend_items, LegendItem))


if __name__ == '__main__':
    unittest.main()

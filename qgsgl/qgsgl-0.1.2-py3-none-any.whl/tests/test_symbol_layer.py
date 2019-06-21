from ..layer import SymbolLayer
from .utils import get_qgis_dir
from qgis.testing import start_app, unittest
from qgis.core import QgsSvgMarkerSymbolLayer, QgsSimpleMarkerSymbolLayer, \
    QgsSimpleMarkerSymbolLayerBase
import os


start_app()


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.style = {'name': os.path.join(get_qgis_dir(),
                                           'svg/arrows/Arrow_01.svg')}
        self.symbol_layer = SymbolLayer(
                        QgsSvgMarkerSymbolLayer.create(self.style))
        self.qgis_symbol_layer = QgsSimpleMarkerSymbolLayer()

    def test_symbol_layer(self):
        self.assertEqual(self.symbol_layer.get_type(), 'symbol')

        res = self.symbol_layer.get_layout_properties()
        self.assertTrue(isinstance(res, dict))
        self.assertEqual(res['icon-image'], 'image')

    def test_supports_symbol_layer(self):
        self.qgis_symbol_layer.setShape(QgsSimpleMarkerSymbolLayerBase.Circle)
        self.assertFalse(self.symbol_layer.supports_symbol_layer(
            self.qgis_symbol_layer))
        self.qgis_symbol_layer.setShape(QgsSimpleMarkerSymbolLayerBase.Star)
        self.assertTrue(self.symbol_layer.supports_symbol_layer(
            self.qgis_symbol_layer))


if __name__ == '__main__':
    unittest.main()

import qgis # NOQA
from qgis.core import QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer, \
    QgsGraduatedSymbolRenderer, QgsMarkerSymbol, QgsRendererCategory, \
    QgsRendererRange, QgsVectorLayer
from qgis.testing import start_app, unittest
from ..converters import LayerConverter
from ..layer import MockLayer


start_app()


class TestLayerConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.single = QgsSingleSymbolRenderer(QgsMarkerSymbol())

        cls.categorized = QgsCategorizedSymbolRenderer()
        cls.categorized.setClassAttribute('widgets')
        cls._add_category(1, 'One')
        cls._add_category(2, 'Two')
        cls._add_category(3, 'Three', False)
        cls._add_category(4, 'Four')
        cls._add_category('', 'Other')

        cls.graduated = QgsGraduatedSymbolRenderer()
        cls.graduated.setClassAttribute('widgets')
        cls._add_range(1, 2, 'One')
        cls._add_range(2, 3, 'Two')
        cls._add_range(3, 4, 'Three', False)
        cls._add_range(5, 6, 'Five')

    @classmethod
    def _add_category(cls, value, label, render=True):
        category = QgsRendererCategory(value, QgsMarkerSymbol(), label, render)
        cls.categorized.addCategory(category)

    @classmethod
    def _add_range(cls, lower, upper, label, render=True):
        range = QgsRendererRange(
            lower, upper, QgsMarkerSymbol(), label, render)
        cls.graduated.addClassRange(range)

    def _create_converter(self, renderer, **kwargs):
        qgis_layer = QgsVectorLayer()
        qgis_layer.setRenderer(renderer)
        kwargs.update({
            'base_id': 'test',
            'visible': True,
            'circle_class': MockLayer,
            'fill_class': MockLayer,
            'line_class': MockLayer,
            'symbol_class': MockLayer,
        })
        return LayerConverter(qgis_layer, 'testsource', 'testlayer', **kwargs)

    def test_get_layer_json(self):
        converter = self._create_converter(self.single)
        options = {
            'filter': ['==', ['get', 'foo'], 'bar'],
            'visible': False,
        }
        layer = converter._get_layer_json(MockLayer(), id='test', **options)
        result = {
            'id': 'test',
            'type': 'mock',
            'source': 'testsource',
            'source-layer': 'testlayer',
            'filter': ['==', ['get', 'foo'], 'bar'],
            'layout': {
                'visibility': 'none'
            }
        }
        self.assertEqual(layer, result)

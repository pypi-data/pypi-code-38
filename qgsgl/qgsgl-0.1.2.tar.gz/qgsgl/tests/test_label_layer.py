from ..layer import LabelLayer
from ..glyphs import default_library
from qgis.testing import start_app, unittest
from .utils import create_layers, set_single_symbol
from qgis.core import QgsMarkerSymbol, QgsVectorLayerSimpleLabeling, \
    QgsPalLayerSettings, QgsTextFormat
from PyQt5.QtGui import QFont


start_app()


class TestLabelLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layers = set_single_symbol(create_layers())

        label = QgsPalLayerSettings()
        label.enabled = True
        label.fieldName = 'name'

        text_format = QgsTextFormat()
        text_format.setFont(QFont("Arial Bold", 12))
        text_format.setSize(12)

        label.setFormat(text_format)
        cls.label = QgsVectorLayerSimpleLabeling(label)

    def setUp(self):
        circle_layer = self.layers[0]
        circle_layer.setLabeling(self.label)
        self.circle_label_layer = LabelLayer(
            circle_layer.renderer().symbol(),
            circle_layer.labeling(),
            font_library=default_library)

        line_layer = self.layers[1]
        line_layer.setLabeling(self.label)
        self.line_label_layer = LabelLayer(
            line_layer.renderer().symbol(),
            line_layer.labeling(),
            font_library=default_library)

    def test_label_layer(self):
        self.assertTrue(isinstance(self.circle_label_layer._qgis_symbol,
                                   QgsMarkerSymbol))
        self.assertTrue(isinstance(self.circle_label_layer._labeling,
                                   QgsVectorLayerSimpleLabeling))
        self.assertTrue(isinstance(self.circle_label_layer._settings,
                                   QgsPalLayerSettings))

    def test_get_layout_properties(self):
        self.assertTrue(
            isinstance(self.circle_label_layer.get_layout_properties(),
                       dict))
        self.assertTrue(
            isinstance(self.line_label_layer.get_layout_properties(),
                       dict))

    def test_get_paint_properties(self):
        self.assertTrue(isinstance(
            self.circle_label_layer.get_paint_properties(), dict))
        self.assertTrue(isinstance(
            self.line_label_layer.get_paint_properties(), dict))

    def test_get_font_type(self):
        self.assertEqual(self.circle_label_layer._font_library.get_font_name(
            'Open Sans',
            QFont.Normal,
            False),
            'Open Sans Regular')


if __name__ == '__main__':
    unittest.main()

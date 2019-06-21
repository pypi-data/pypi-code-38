from ..sprite import SpriteImage, SpritePixmap
from .utils import get_qgis_dir
import os
from qgis.testing import start_app, unittest
from qgis.core import QgsSvgMarkerSymbolLayer, QgsMapSettings


start_app()


class TestSpriteImage(unittest.TestCase):
    def setUp(self):
        self.style = {'name': os.path.join(get_qgis_dir(),
                                           'svg/arrows/Arrow_01.svg')}
        self.image_id = 'image_1'
        self.symbol_layer = QgsSvgMarkerSymbolLayer.create(self.style)
        self.sprite_image = SpriteImage(self.symbol_layer, self.image_id)

    def test_render(self):
        self.assertTrue(isinstance(self.sprite_image.render(), SpritePixmap))

    def test_get_ratio_factor(self):
        map_setting = QgsMapSettings()
        ratio = map_setting.devicePixelRatio()
        self.assertEqual(self.sprite_image._get_ratio_factor(1), ratio)

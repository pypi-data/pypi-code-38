from ..sprite import SpriteImage, SpritePixmap
from .utils import get_qgis_dir
import os
from qgis.testing import start_app, unittest
from qgis.core import QgsSvgMarkerSymbolLayer
from PyQt5.QtCore import QSize


start_app()


class TestSpritePixmap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.style = {'name': os.path.join(get_qgis_dir(),
                                          'svg/arrows/Arrow_01.svg')}
        cls.image_id = 'image_1'
        cls.symbol_layer = QgsSvgMarkerSymbolLayer.create(cls.style)
        sprite_image = SpriteImage(cls.symbol_layer, cls.image_id)
        cls.sprite_pixmap = sprite_image.render(2)

        cls.style_2 = {'name': os.path.join(get_qgis_dir(),
                                            'svg/arrows/Arrow_02.svg')}
        cls.image_id_2 = 'image_2'
        cls.symbol_layer_2 = QgsSvgMarkerSymbolLayer.create(cls.style_2)
        sprite_image_2 = SpriteImage(cls.symbol_layer_2, cls.image_id_2)
        cls.sprite_pixmap_2 = sprite_image_2.render()

        cls.image_list = [cls.sprite_pixmap_2, cls.sprite_pixmap]

    def test_simple(self):
        self.assertTrue(isinstance(self.sprite_pixmap, SpritePixmap))

    def test_size(self):
        self.assertTrue(isinstance(self.sprite_pixmap.size, QSize))

    def test_height(self):
        self.assertTrue(isinstance(self.sprite_pixmap.height, int))
        self.assertTrue(isinstance(self.sprite_pixmap_2.height, int))

    def test_width(self):
        self.assertTrue(isinstance(self.sprite_pixmap.width, int))

    def test_compare(self):
        self.assertTrue(self.sprite_pixmap > self.sprite_pixmap_2)
        self.assertFalse(self.sprite_pixmap < self.sprite_pixmap_2)

    def test_order(self):
        self.image_list.sort(reverse=True)
        self.assertTrue(self.image_list[0].height > self.image_list[1].height)

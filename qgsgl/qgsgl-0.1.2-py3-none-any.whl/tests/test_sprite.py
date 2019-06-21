from ..sprite import Sprite, SpriteImage
from .utils import get_qgis_dir
import os
from qgis.testing import start_app, unittest
from qgis.core import QgsSvgMarkerSymbolLayer
from tempfile import TemporaryDirectory


start_app()


class TestSprite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out_name = 'test'
        cls.style = {'name': os.path.join(get_qgis_dir(),
                                          'svg/arrows/Arrow_01.svg')}
        cls.style_2 = {'name': os.path.join(get_qgis_dir(),
                                            'svg/arrows/Arrow_02.svg')}
        cls.style_3 = {'name': os.path.join(get_qgis_dir(),
                                            'svg/arrows/Arrow_03.svg')}
        cls.image_id = 'image_1'
        cls.image_id_2 = 'image_2'
        cls.image_id_3 = 'image_3'
        cls.sprite = Sprite()
        cls.sprite_image = SpriteImage(
                        QgsSvgMarkerSymbolLayer.create(cls.style),
                        cls.image_id)
        cls.sprite_image_2 = SpriteImage(
                        QgsSvgMarkerSymbolLayer.create(cls.style_2),
                        cls.image_id_2)
        cls.sprite_image_3 = SpriteImage(
                        QgsSvgMarkerSymbolLayer.create(cls.style_3),
                        cls.image_id_3)

    def setUp(self):
        self.sprite = Sprite()
        self.sprite.add_image(self.sprite_image_2)
        self.sprite.add_image(self.sprite_image_3)
        self.sprite.add_image(self.sprite_image)

    def test_add_image(self):
        self.sprite.add_image(self.sprite_image)
        self.assertTrue(isinstance(self.sprite._sprite_images[0], SpriteImage))

    def test_render(self):
        with TemporaryDirectory() as temp_dir:
            self.sprite.render(temp_dir, scale=2)
            self.assertTrue(os.path.isfile(
                os.path.join(temp_dir, 'sprite@2x.png')
            ))
            self.assertTrue(os.path.isfile(
                os.path.join(temp_dir, 'sprite@2x.json')
            ))


if __name__ == '__main__':
    unittest.main()

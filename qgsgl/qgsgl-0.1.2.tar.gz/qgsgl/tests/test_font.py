from ..glyphs import FontLibrary
from qgis.testing import start_app, unittest
from PyQt5.QtGui import QFont


start_app()


class TestLayer(unittest.TestCase):
    def setUp(self):
        self.font = FontLibrary(default_face='Open Sans')

    def test_font(self):
        self.assertTrue(isinstance(self.font, FontLibrary))
        self.assertEqual(self.font._default_face, 'Open Sans')

    def test_add_font(self):
        self.assertEqual(len(self.font._font_library), 0)
        face = 'Open Sans'
        self.font.add_font('Open Sans Light Italic',
                           face,
                           [QFont.Thin, QFont.ExtraLight, QFont.Light],
                           True)
        self.assertEqual(len(self.font._font_library[face]), 3)

    def test_additional_face(self):
        self.font.add_font('Open Sans Light Italic',
                           'Open Sans',
                           [QFont.Thin, QFont.ExtraLight, QFont.Light],
                           True)
        self.font.add_font('Arial Black Light',
                           'Arial',
                           [QFont.Thin, QFont.Light],
                           False)
        self.assertEqual(len(self.font._font_library), 2)

    def test_get_font_name(self):
        self.font.add_font('Open Sans Light Italic',
                           'Open Sans',
                           [QFont.Thin, QFont.ExtraLight, QFont.Light],
                           True)
        self.assertEqual(self.font.get_font_name('Open Sans',
                                                 QFont.Thin,
                                                 True),
                         'Open Sans Light Italic')

        self.assertEqual(self.font.get_font_name('Font Not Available',
                                                 QFont.Thin,
                                                 True),
                         'Open Sans Light Italic')

    def test_available_face(self):
        self.font.add_font('Open Sans Light Italic',
                           'Open Sans',
                           [QFont.Thin, QFont.ExtraLight, QFont.Light],
                           True)
        self.font.add_font('Arial Black Light',
                           'Arial',
                           [QFont.Thin, QFont.Light],
                           False)
        self.assertEqual(self.font.available_face, ['Open Sans', 'Arial'])


if __name__ == '__main__':
    unittest.main()

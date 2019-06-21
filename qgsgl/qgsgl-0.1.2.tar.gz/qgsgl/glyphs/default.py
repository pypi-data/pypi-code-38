from .library import FontLibrary
from PyQt5.QtGui import QFont

font_library = FontLibrary(default_face='Open Sans')
# Light
font_library.add_font(
    'Open Sans Light Italic',
    'Open Sans',
    [QFont.Thin, QFont.ExtraLight, QFont.Light],
    True
)
font_library.add_font(
    'Open Sans Light',
    'Open Sans',
    [QFont.Thin, QFont.ExtraLight, QFont.Light],
    False
)
# Regular
font_library.add_font(
    'Open Sans Italic',
    'Open Sans',
    [QFont.Normal, QFont.Medium],
    True
)
font_library.add_font(
    'Open Sans Regular',
    'Open Sans',
    [QFont.Normal, QFont.Medium],
    False
)
# Semi Bold
font_library.add_font(
    'Open Sans SemiBold Italic',
    'Open Sans',
    [QFont.DemiBold],
    True
)
font_library.add_font(
    'Open Sans SemiBold',
    'Open Sans',
    [QFont.DemiBold],
    False
)
# Bold
font_library.add_font(
    'Open Sans Bold Italic',
    'Open Sans',
    [QFont.Bold],
    True
)
font_library.add_font(
    'Open Sans Bold',
    'Open Sans',
    [QFont.Bold],
    False
)
# Extra-Bold
font_library.add_font(
    'Open Sans ExtraBold Italic',
    'Open Sans',
    [QFont.ExtraBold, QFont.Black],
    True
)
font_library.add_font(
    'Open Sans ExtraBold',
    'Open Sans',
    [QFont.ExtraBold, QFont.Black],
    False
)

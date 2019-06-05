import os

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
FONTS_PATH = os.path.join(CURRENT_PATH, 'fonts', 'pingfang.ttf')


def test_font():
    if os.path.isfile(FONTS_PATH):
        print('exists~~~~')
    else:
        print('ops~~~~~')

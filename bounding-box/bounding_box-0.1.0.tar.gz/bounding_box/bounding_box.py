from __future__ import division as _division
from __future__ import print_function as _print_function

import os as _os
import os.path as _path
import cv2 as _cv2
import numpy as _np
from hashlib import md5 as _md5

_LOC = _path.realpath(_path.join(_os.getcwd(),_path.dirname(__file__)))

#https://clrs.cc/
_COLOR_NAME_TO_RGB = dict(navy=((0, 31, 63), (128, 192, 255)),
                         blue=((0, 115, 217), (179, 219, 255)),
                         aqua=((127, 219, 255), (0, 72, 102)),
                         teal=((57, 204, 204), (0, 0, 0)),
                         olive=((61, 153, 112), (23, 55, 40)),
                         green=((46, 204, 64), (44, 198, 61)),
                         lime=((1, 255, 112), (0, 102, 45)),
                         yellow=((255, 220, 3), (102, 88, 0)),
                         orange=((255, 133, 28), (102, 49, 0)),
                         red=((254, 65, 54), (128, 6, 1)),
                         maroon=((133, 20, 75), (235, 121, 177)),
                         fuchsia=((240, 17, 190), (142, 9, 112)),
                         purple=((177, 14, 201), (239, 169, 249)),
                         black=((16, 16, 16), (221, 221, 221)),
                         gray=((170, 171, 170), (0, 0, 0)),
                         silver=((221, 221, 221), (0, 0, 0)))

_COLOR_NAMES = list(_COLOR_NAME_TO_RGB)

_DEFAULT_COLOR_NAME = "green"

_FONT_PATH = _os.path.join(_LOC, "Ubuntu-B.ttf")
_FONT_HEIGHT = 15
_FT = _cv2.freetype.createFreeType2()
_FT.loadFontData(_FONT_PATH, 0)

def _rgb_to_bgr(color):
    return color[2], color[1], color[0]

def add_bounding_box(image, left, top, right, bottom, label=None, color=None):
    if type(image) is not _np.ndarray:
        raise TypeError("'image' parameter must be a numpy.ndarray")

    if False in (type(item) is int for item in (left, top, right, bottom)):
        raise TypeError("'left', 'top', 'right', 'bottom' must be int")

    if label and type(label) is not str:
        raise TypeError("'label' must be a str")

    if label and not color:
        hex_digest = _md5(label.encode()).hexdigest()
        color_index = int(hex_digest, 16) % len(_COLOR_NAME_TO_RGB)
        color = _COLOR_NAMES[color_index]

    if not color:
        color = _DEFAULT_COLOR_NAME

    if type(color) is not str:
        raise TypeError("'color' must be a str")

    if color not in _COLOR_NAME_TO_RGB:
        msg = "'color' must be one of " + ", ".join(_COLOR_NAME_TO_RGB)
        raise ValueError(msg)

    colors = [_rgb_to_bgr(item) for item in _COLOR_NAME_TO_RGB[color]]
    color, color_text = colors

    _cv2.rectangle(image, (left, top), (right, bottom), color, 2)

    if label:
        label_left = left - 1
        label_top = top - _FONT_HEIGHT - _FONT_HEIGHT // 3
        label_right = left + _FT.getTextSize(label, _FONT_HEIGHT, -1)[0][0]
        label_bottom = top

        if label_top < 0:
            label_top = top
            label_bottom = top + _FONT_HEIGHT + _FONT_HEIGHT // 3

        text_left = left
        text_bottom = label_bottom - _FONT_HEIGHT // 3

        _cv2.rectangle(image, (label_left, label_top),
                      (label_right, label_bottom), color, -1)

        _FT.putText(image, label, (text_left, text_bottom), _FONT_HEIGHT,
                   color_text, -1, _cv2.LINE_AA, True)

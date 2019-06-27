#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# CSS color parsing
# Copyright (C) 2009-2019 Jérome-Poisson

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat.core.log import getLogger

log = getLogger(__name__)


CSS_COLORS = {
    u"black": u"000000",
    u"silver": u"c0c0c0",
    u"gray": u"808080",
    u"white": u"ffffff",
    u"maroon": u"800000",
    u"red": u"ff0000",
    u"purple": u"800080",
    u"fuchsia": u"ff00ff",
    u"green": u"008000",
    u"lime": u"00ff00",
    u"olive": u"808000",
    u"yellow": u"ffff00",
    u"navy": u"000080",
    u"blue": u"0000ff",
    u"teal": u"008080",
    u"aqua": u"00ffff",
    u"orange": u"ffa500",
    u"aliceblue": u"f0f8ff",
    u"antiquewhite": u"faebd7",
    u"aquamarine": u"7fffd4",
    u"azure": u"f0ffff",
    u"beige": u"f5f5dc",
    u"bisque": u"ffe4c4",
    u"blanchedalmond": u"ffebcd",
    u"blueviolet": u"8a2be2",
    u"brown": u"a52a2a",
    u"burlywood": u"deb887",
    u"cadetblue": u"5f9ea0",
    u"chartreuse": u"7fff00",
    u"chocolate": u"d2691e",
    u"coral": u"ff7f50",
    u"cornflowerblue": u"6495ed",
    u"cornsilk": u"fff8dc",
    u"crimson": u"dc143c",
    u"darkblue": u"00008b",
    u"darkcyan": u"008b8b",
    u"darkgoldenrod": u"b8860b",
    u"darkgray": u"a9a9a9",
    u"darkgreen": u"006400",
    u"darkgrey": u"a9a9a9",
    u"darkkhaki": u"bdb76b",
    u"darkmagenta": u"8b008b",
    u"darkolivegreen": u"556b2f",
    u"darkorange": u"ff8c00",
    u"darkorchid": u"9932cc",
    u"darkred": u"8b0000",
    u"darksalmon": u"e9967a",
    u"darkseagreen": u"8fbc8f",
    u"darkslateblue": u"483d8b",
    u"darkslategray": u"2f4f4f",
    u"darkslategrey": u"2f4f4f",
    u"darkturquoise": u"00ced1",
    u"darkviolet": u"9400d3",
    u"deeppink": u"ff1493",
    u"deepskyblue": u"00bfff",
    u"dimgray": u"696969",
    u"dimgrey": u"696969",
    u"dodgerblue": u"1e90ff",
    u"firebrick": u"b22222",
    u"floralwhite": u"fffaf0",
    u"forestgreen": u"228b22",
    u"gainsboro": u"dcdcdc",
    u"ghostwhite": u"f8f8ff",
    u"gold": u"ffd700",
    u"goldenrod": u"daa520",
    u"greenyellow": u"adff2f",
    u"grey": u"808080",
    u"honeydew": u"f0fff0",
    u"hotpink": u"ff69b4",
    u"indianred": u"cd5c5c",
    u"indigo": u"4b0082",
    u"ivory": u"fffff0",
    u"khaki": u"f0e68c",
    u"lavender": u"e6e6fa",
    u"lavenderblush": u"fff0f5",
    u"lawngreen": u"7cfc00",
    u"lemonchiffon": u"fffacd",
    u"lightblue": u"add8e6",
    u"lightcoral": u"f08080",
    u"lightcyan": u"e0ffff",
    u"lightgoldenrodyellow": u"fafad2",
    u"lightgray": u"d3d3d3",
    u"lightgreen": u"90ee90",
    u"lightgrey": u"d3d3d3",
    u"lightpink": u"ffb6c1",
    u"lightsalmon": u"ffa07a",
    u"lightseagreen": u"20b2aa",
    u"lightskyblue": u"87cefa",
    u"lightslategray": u"778899",
    u"lightslategrey": u"778899",
    u"lightsteelblue": u"b0c4de",
    u"lightyellow": u"ffffe0",
    u"limegreen": u"32cd32",
    u"linen": u"faf0e6",
    u"mediumaquamarine": u"66cdaa",
    u"mediumblue": u"0000cd",
    u"mediumorchid": u"ba55d3",
    u"mediumpurple": u"9370db",
    u"mediumseagreen": u"3cb371",
    u"mediumslateblue": u"7b68ee",
    u"mediumspringgreen": u"00fa9a",
    u"mediumturquoise": u"48d1cc",
    u"mediumvioletred": u"c71585",
    u"midnightblue": u"191970",
    u"mintcream": u"f5fffa",
    u"mistyrose": u"ffe4e1",
    u"moccasin": u"ffe4b5",
    u"navajowhite": u"ffdead",
    u"oldlace": u"fdf5e6",
    u"olivedrab": u"6b8e23",
    u"orangered": u"ff4500",
    u"orchid": u"da70d6",
    u"palegoldenrod": u"eee8aa",
    u"palegreen": u"98fb98",
    u"paleturquoise": u"afeeee",
    u"palevioletred": u"db7093",
    u"papayawhip": u"ffefd5",
    u"peachpuff": u"ffdab9",
    u"peru": u"cd853f",
    u"pink": u"ffc0cb",
    u"plum": u"dda0dd",
    u"powderblue": u"b0e0e6",
    u"rosybrown": u"bc8f8f",
    u"royalblue": u"4169e1",
    u"saddlebrown": u"8b4513",
    u"salmon": u"fa8072",
    u"sandybrown": u"f4a460",
    u"seagreen": u"2e8b57",
    u"seashell": u"fff5ee",
    u"sienna": u"a0522d",
    u"skyblue": u"87ceeb",
    u"slateblue": u"6a5acd",
    u"slategray": u"708090",
    u"slategrey": u"708090",
    u"snow": u"fffafa",
    u"springgreen": u"00ff7f",
    u"steelblue": u"4682b4",
    u"tan": u"d2b48c",
    u"thistle": u"d8bfd8",
    u"tomato": u"ff6347",
    u"turquoise": u"40e0d0",
    u"violet": u"ee82ee",
    u"wheat": u"f5deb3",
    u"whitesmoke": u"f5f5f5",
    u"yellowgreen": u"9acd32",
    u"rebeccapurple": u"663399",
}
DEFAULT = u"000000"


def parse(raw_value, as_string=True):
    """parse CSS color value and return normalised value

    @param raw_value(unicode): CSS value
    @param as_string(bool): if True return a string,
        else return a tuple of int
    @return (unicode, tuple): normalised value
        if as_string is True, value is 3 or 4 hex words (e.g. u"ff00aabb")
        else value is a 3 or 4 tuple of int (e.g.: (255, 0, 170, 187)).
        If present, the 4th value is the alpha channel
        If value can't be parsed, a warning message is logged, and DEFAULT is returned
    """
    raw_value = raw_value.strip().lower()
    if raw_value.startswith(u"#"):
        # we have a hexadecimal value
        str_value = raw_value[1:]
        if len(raw_value) in (3, 4):
            str_value = u"".join([2 * v for v in str_value])
    elif raw_value.startswith(u"rgb"):
        left_p = raw_value.find(u"(")
        right_p = raw_value.find(u")")
        rgb_values = [v.strip() for v in raw_value[left_p + 1 : right_p].split(",")]
        expected_len = 4 if raw_value.startswith(u"rgba") else 3
        if len(rgb_values) != expected_len:
            log.warning(u"incorrect value: {}".format(raw_value))
            str_value = DEFAULT
        else:
            int_values = []
            for rgb_v in rgb_values:
                p_idx = rgb_v.find(u"%")
                if p_idx == -1:
                    # base 10 value
                    try:
                        int_v = int(rgb_v)
                        if int_v > 255:
                            raise ValueError(u"value exceed 255")
                        int_values.append(int_v)
                    except ValueError:
                        log.warning(u"invalid int: {}".format(rgb_v))
                        int_values.append(0)
                else:
                    # percentage
                    try:
                        int_v = int(int(rgb_v[:p_idx]) / 100.0 * 255)
                        if int_v > 255:
                            raise ValueError(u"value exceed 255")
                        int_values.append(int_v)
                    except ValueError:
                        log.warning(u"invalid percent value: {}".format(rgb_v))
                        int_values.append(0)
            str_value = u"".join([u"{:02x}".format(v) for v in int_values])
    elif raw_value.startswith(u"hsl"):
        log.warning(u"hue-saturation-lightness not handled yet")  # TODO
        str_value = DEFAULT
    else:
        try:
            str_value = CSS_COLORS[raw_value]
        except KeyError:
            log.warning(u"unrecognised format: {}".format(raw_value))
            str_value = DEFAULT

    if as_string:
        return str_value
    else:
        return tuple(
            [
                int(str_value[i] + str_value[i + 1], 16)
                for i in xrange(0, len(str_value), 2)
            ]
        )

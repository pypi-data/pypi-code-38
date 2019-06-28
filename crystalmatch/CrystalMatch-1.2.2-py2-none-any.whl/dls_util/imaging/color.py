
from pkg_resources import require
require("numpy>=1.11.1")
from random import randint
class Color:
    """ Represents a color stored as an RGB or RGBA value.

    """
    SEP = ","
    CONSTRUCTOR_ERROR = "Values must be integers in range 0-255"
    STRING_PARSE_ERROR = "Input string must be 3 or 4 integers (0-255) separated by '{}'".format(SEP)

    def __init__(self, r, g, b, a=255):
        try:
            r, g, b, a = int(r), int(g), int(b), int(a)
        except TypeError:
            raise TypeError(self.CONSTRUCTOR_ERROR)
        except ValueError:
            raise ValueError(self.CONSTRUCTOR_ERROR)

        for val in [r, g, b, a]:
            if val < 0 or val > 255:
                raise ValueError(self.CONSTRUCTOR_ERROR)

        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def __str__(self):
        return "{1}{0}{2}{0}{3}{0}{4}".format(self.SEP, self.r, self.g, self.b, self.a)

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(self.__class__.__name__, self.r, self.g, self.b, self.a)

    def __eq__(self, other):
        if not isinstance(other, Color):
            raise TypeError("Attempt to match non-Colour object with " + repr(self))
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    def bgra(self):
        """ Return color as a BGRA tuple. (Useful for working with OpenCV). """
        return self.b, self.g, self.r, self.a

    def bgr(self):
        """ Return color as a BGR tuple. (Useful for working with OpenCV). """
        return self.b, self.g, self.r

    def mono(self):
        """ Perform conversion to 8-bit grayscale by non-linear Luma encoding.
        ref: https://en.wikipedia.org/wiki/Grayscale#Luma_coding_in_video_systems """
        return int(round(0.299*self.r + 0.587*self.g + 0.114*self.b))

    def to_hex(self):
        """ Return a hexadecimal representation of the color. """
        hex_str = '#'
        for val in [self.r, self.g, self.b]:
            hex_str += '{:02x}'.format(val)

        return hex_str

    @staticmethod
    def from_string(string, sep=SEP):
        """ Create a new Color object by interpreting a string. The string must contain 3 or 4 8-bit
        values (0-255), separated by the sep character (comma by default). The values should be
        ordered as RGB(A). """
        if string is None:
            raise TypeError(Color.STRING_PARSE_ERROR)
        tokens = string.split(sep)

        if len(tokens) == 3:
            r, g, b = tuple(tokens)
            color = Color(r, g, b)
        elif len(tokens) == 4:
            r, g, b, a = tuple(tokens)
            color = Color(r, g, b, a)
        else:
            raise ValueError(Color.STRING_PARSE_ERROR)

        return color

    @staticmethod
    def random():
        return Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)

    @staticmethod
    def transparent_black(): return Color(0, 0, 0, 0)  # pragma: no cover

    @staticmethod
    def transparent_white(): return Color(255, 255, 255, 0)  # pragma: no cover

    @staticmethod
    def white(): return Color(255, 255, 255)  # pragma: no cover

    @staticmethod
    def black(): return Color(0, 0, 0)  # pragma: no cover

    @staticmethod
    def grey(): return Color(128, 128, 128)  # pragma: no cover

    @staticmethod
    def blue(): return Color(0, 0, 255)  # pragma: no cover

    @staticmethod
    def red(): return Color(255, 0, 0)  # pragma: no cover

    @staticmethod
    def green(): return Color(0, 255, 0)  # pragma: no cover

    @staticmethod
    def yellow(): return Color(255, 255, 0)  # pragma: no cover

    @staticmethod
    def cyan(): return Color(0, 255, 255)  # pragma: no cover

    @staticmethod
    def magenta(): return Color(255, 0, 255)  # pragma: no cover

    @staticmethod
    def orange(): return Color(255, 128, 0)  # pragma: no cover

    @staticmethod
    def purple(): return Color(128, 0, 255)  # pragma: no cover

    @staticmethod
    def slate_gray(): return Color(108, 123, 139)  # pragma: no cover

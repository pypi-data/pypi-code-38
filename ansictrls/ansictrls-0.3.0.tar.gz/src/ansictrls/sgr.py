import re
from contextlib import suppress
from functools import lru_cache
from types import new_class

from .ctrls import CS

_SGRRE = re.compile(r'\x1b\[[\d;]*m')

_SGR_ATTRS = dict(
    Bold=(1, 22),
    Faint=(2, 22),
    Italic=(3, 23),
    Underlined=(4, 24),
    Blink=(5, 25),
    Inverse=(7, 27),
    Crossedout=(9, 29),
    Overlined=(53, 55),
    Reset=(0, 0),
    FgBlack=(30, 90),
    FgRed=(31, 91),
    FgGreen=(32, 92),
    FgYellow=(33, 93),
    FgBlue=(34, 94),
    FgMagenta=(35, 95),
    FgCyan=(36, 96),
    FgWhite=(37, 97),
    FgDefault=(39, 39),
    BgBlack=(40, 100),
    BgRed=(41, 101),
    BgGreen=(42, 102),
    BgYellow=(43, 103),
    BgBlue=(44, 104),
    BgMagenta=(45, 105),
    BgCyan=(46, 106),
    BgWhite=(47, 107),
    BgDefault=(49, 49),
)


class _SGRParam:
    pass


class _SGRAttr(int, _SGRParam):
    def __new__(cls, name, value, invert):
        obj = int.__new__(cls, value)
        obj._name = name
        obj._invert = int.__new__(cls, invert)
        obj._invert._name = '~' + name
        obj._invert._invert = obj
        return obj

    def __invert__(self):
        return self._invert

    def __repr__(self):
        return '<%s: %d>' % (self._name, self)

    def __str__(self):
        return '%s' % self._name


def _sgr_cb(ns):
    for k, v in _SGR_ATTRS.items():
        ns[k] = _SGRAttr('SGR.' + k, *v)


SGR = new_class('SGR', exec_body=_sgr_cb)
SGR.__doc__ = 'SGR attributes.'


class _SGRColor(tuple, _SGRParam):
    def __new__(cls, name, *args):
        obj = tuple.__new__(cls, args)
        obj._name = name
        return obj

    def __repr__(self):
        return '<SGR.%sColor: %s>' % (self._name, tuple(self))

    def __str__(self):
        return 'SGR.%sColor%s' % (self._name, self[2:])


def _color(*args):
    with suppress(Exception):
        if len(args) == 1:
            if isinstance(args[0], int) and 0 <= args[0] <= 255:
                return 5, args[0]
            elif len(args[0]) in (4, 7) and args[0].startswith('#'):
                if len(args[0]) == 4:
                    s = ''.join(x + x for x in args[0][1:])
                else:
                    s = args[0][1:]
                return (2,) + tuple(int(s[i:i + 2], 16)
                                    for i in range(0, len(s), 2))
        elif len(args) == 3 and all(0 <= x <= 255 for x in args):
            return (2,) + args
    raise ValueError('Invalid arguments for color: %s' % str(args))


def fg(*args):
    """Return SGR parameters for foreground :ref:`color <ref-intro-colors>`.

    :param args: arguments for color
    :return: color for use with :attr:`CS.SGR` or :func:`sgr_print`
    """
    return _SGRColor('Fg', 38, *_color(*args))


def bg(*args):
    """Return SGR parameters for background :ref:`color <ref-intro-colors>`.

    :param args: arguments for color
    :return: color for use with :attr:`CS.SGR` or :func:`sgr_print`
    """
    return _SGRColor('Bg', 48, *_color(*args))


@lru_cache()
def text(s):
    """Return the plain text without the SGR control sequences.

    :param str s: the string with SGR control sequences
    :return: plain text
    :rtype: str
    """
    return ''.join(_SGRRE.split(s))


def len_diff(s):
    r"""Return the difference between ``len(s)`` and ``len(text(s))``.

    Useful for adjusting the text on the screen::

       s = sgr_string(SGR.Bold, SGR.FgRed, 'ABC')
       w = 20
       print(repr(s))
       print(text(s))
       print('1234567890' * 2)  # numbering 20 columns
       print(s.center(w, '.'))
       print(s.center(w + len_diff(s), '.'))
       print('%*s' % (w, s))
       print('%*s' % (w + len_diff(s), s))
       print('{:.^{width}}'.format(s, width=w))
       print('{:.^{width}}'.format(s, width=w + len_diff(s)))

    .. raw:: html

       <pre style="color:#FFFFFF;background-color:#000000">
       &apos;\x1b[1;31mABC\x1b[0m&apos;
       ABC
       12345678901234567890
       ...<font color="#FF5555"><b>ABC</b></font>...
       .........<font color="#FF5555"><b>ABC</b></font>........
             <font color="#FF5555"><b>ABC</b></font>
                        <font color="#FF5555"><b>ABC</b></font>
       ...<font color="#FF5555"><b>ABC</b></font>...
       ........<font color="#FF5555"><b>ABC</b></font>.........
       </pre>

    :param str s: the string with SGR control sequences
    :return: difference of the lengths of ``s`` and the visible text
    :rtype: int
    """
    return len(s) - len(text(s))


def sgr_string(*args, reset=True):
    r"""Build a string with SGR control sequences.

    Those arguments that are :class:`SGR` attributes or the result of
    the :func:`fg` or :func:`bg` functions will be passed as parameters to
    :attr:`CS.SGR`, all others will be converted to strings. Than
    all elements will be concatenated and returned as a string.

    >>> CS.SGR % (SGR.Bold, SGR.FgRed) + 'ABC' + CS.SGR % SGR.Reset
    '\x1b[1;31mABC\x1b[0m'
    >>> sgr_string(SGR.Bold, SGR.FgRed, 'ABC')
    '\x1b[1;31mABC\x1b[0m'

    :param args: arguments
    :param bool reset: if ``True`` all SGR attributes will be reset to normal
                       at the end of the string
    :return: a string
    :rtype: str
    """
    r = []
    p = []
    for arg in args:
        if isinstance(arg, _SGRParam):
            p.append(arg)
        else:
            if p:
                r.append(CS.SGR % tuple(p))
                p.clear()
            r.append(arg)
    if reset:
        p.append(SGR.Reset)
    if p:
        r.append(CS.SGR % tuple(p))
    return ''.join(map(str, r))


def sgr_print(*args, reset=True, end='\n', flush=False):
    """Print a string with SGR control sequences.

    See function :func:`sgr_string`.

    :param args: arguments (see: :func:`sgr_string`)
    :param bool reset: if ``True`` all SGR attributes will be reset to normal
                       at the end of the string
    :param str end: see built-in function :func:`print`
    :param bool flush: see built-in function :func:`print`
    """
    print(sgr_string(*args, reset=reset), sep='', end=end, flush=flush)

import re
from contextlib import suppress

from .ctrls import CS
from .sgr import SGR, fg, bg

_ATTRS_GRP_PATTERN = '(?P<attrs>.*?)'
_DFLT_ATTRS_START = '#['
_DFLT_ATTRS_END = ']'
_ATTRS = {'bd': SGR.Bold,
          'ft': SGR.Faint,
          'it': SGR.Italic,
          'ul': SGR.Underlined,
          'bk': SGR.Blink,
          'iv': SGR.Inverse,
          'co': SGR.Crossedout,
          'ol': SGR.Overlined,
          '': SGR.Reset,
          'reset': SGR.Reset}


def set_attributes_delimiters(start=_DFLT_ATTRS_START, end=_DFLT_ATTRS_END):
    """Set the delimiters for attributes.

    See: :ref:`specification string <ref-intro-spec>`.

    :param str start: start delimiter
    :param str end: end delimiter
    :raise TypeError: if one of the delimiters is not a string
    :raise ValueError: if one of the delimiters is an empty string
    """
    global _attrs_re
    if not (start and end):
        raise ValueError(
            'at least one delimiter %r/%r not allowed' % (start, end))
    _attrs_re = re.compile(re.escape(start) + _ATTRS_GRP_PATTERN +
                           re.escape(end))


set_attributes_delimiters()  # set the defaults


def parse(spec, strict=False):
    """Parse the :ref:`specification string <ref-intro-spec>`.

    :param str spec: the specification string
    :param bool strict: if ``False`` unknown attributes will be ignored
    :return: string with SGR control sequences
    :rtype: str
    :raises ValueError: if ``strict=True`` and an unkown attribute
                        is encountered
    """
    tokens = []
    pos = 0
    for m in _attrs_re.finditer(spec):
        start, end = m.span()
        if pos != start:
            tokens.append(spec[pos:start])
        pos = end
        params = _get_params(m['attrs'], strict)
        if params:
            tokens.append(CS.SGR % params)
    if pos != len(spec):
        tokens.append(spec[pos:])
    return ''.join(tokens)


def _get_params(s, strict):
    params = []
    for x in map(str.strip, s.lower().split(';')):
        if x.startswith('fg') or x.startswith('bg'):
            params.append(_get_color(x))
            continue
        if x.startswith('not'):
            not_ = True
            x = x[3:].lstrip()
        else:
            not_ = False
        attr = _ATTRS.get(x)
        if attr is not None:
            params.append(~attr if not_ else attr)
        else:
            params.append(None)
    if strict and None in params:
        raise ValueError('Error in attributes: "%s"' % s)
    return tuple(param for param in params if param is not None)


def _get_color(s):
    is_fg = s.startswith('fg')
    s = s[2:].lstrip()
    if not s or s == 'default':
        return SGR.FgDefault if is_fg else SGR.BgDefault
    with suppress(Exception):
        if s.startswith('#'):
            if len(s) in (4, 7):
                if len(s) == 4:
                    s = ''.join(x + x for x in s[1:])
                else:
                    s = s[1:]
                t = tuple(int(s[i:i + 2], 16) for i in range(0, len(s), 2))
                if all(0 <= n for n in t):
                    return fg(*t) if is_fg else bg(*t)
        elif ',' in s:
            t = tuple(int(x) for x in s.split(',', 2) if 0 <= int(x) <= 255)
            if len(t) == 3:
                return fg(*t) if is_fg else bg(*t)
        elif s.isdigit():
            if 0 <= int(s) <= 255:
                return fg(int(s)) if is_fg else bg(int(s))
        else:
            if s.startswith('bright'):
                bright = True
                s = s[6:].lstrip()
            else:
                bright = False
            clr = getattr(SGR, ('Fg' if is_fg else 'Bg') + s.capitalize())
            return ~clr if bright else clr
    return None

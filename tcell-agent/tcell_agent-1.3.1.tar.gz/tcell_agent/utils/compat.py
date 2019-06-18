import sys

from functools import partial


PY2 = sys.version_info[0] == 2


if PY2:
    text_type = unicode  # noqa Python>3.2 pylint: disable=undefined-variable
    string_classes = basestring  # noqa Python>3.2 pylint: disable=undefined-variable

    from cgi import escape as cgi_escape
    html_escape = partial(cgi_escape, quote=True)
else:
    text_type = str
    string_classes = (str, bytes)

    from html import escape as html_escape


def to_bytes(x):
    if isinstance(x, text_type):
        return x.encode("utf-8")
    if not isinstance(x, bytes):
        raise TypeError("Bytes or string expected")

    return x


def a_string(s):
    return isinstance(s, string_classes)


def escape_html(s):
    return html_escape(s)

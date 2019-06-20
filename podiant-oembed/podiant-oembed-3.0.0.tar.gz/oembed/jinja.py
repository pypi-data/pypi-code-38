from .parse import parse_html


def oembed(value):
    return parse_html(value, ajax=False)

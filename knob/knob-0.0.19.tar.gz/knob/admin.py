# -*- coding:utf-8 -*-
from django.utils.html import format_html


__all__ = ['rich_tag']


def rich_tag(text, color=None, bold=False, italic=False, hint=None, tag='span'):
    opts = {
        "text": text,
        "color": "color: {};".format(color) if color else "",
        "tag": tag,
        "bold": " font-weight: bold;" if bold else "",
        "italic": " font-style: italic;" if italic else "",
    }

    if hint:
        opts['hint'] = hint
        tmpl = u'<{tag} style="{color}{bold}{italic}" title="{hint}">{text}</{tag}>'
    else:
        tmpl = u'<{tag} style="{color}{bold}{italic}">{text}</{tag}>'

    return format_html(tmpl, **opts)

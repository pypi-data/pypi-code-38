# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import re
from django.utils.six.moves.html_parser import HTMLParser

from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def compress_whitespace(txt):
    try:
        txt = txt.strip()
        txt = re.sub(r'\s+', ' ', txt)
    except Exception:
        # In case of error, filters should return either the
        # original input or an empty string – whichever makes more sense.
        pass
    return txt


@register.filter(is_safe=False)
@stringfilter
def re_isplit(value, arg=""):
    return re.split(arg, value, flags=re.I)


@register.filter(is_safe=False)
@stringfilter
def re_split(value, arg=""):
    return re.split(arg, value)


@register.filter(is_safe=False)
@stringfilter
def decode_htmlentities(value):
    """&pound; will become £ and all over entities too."""
    try:
        h = HTMLParser()
        return h.unescape(value)
    except Exception:
        return value
    

@register.filter(is_safe=False)
@stringfilter
def links_to_text(value):
    """Extracts hyperlinks from html for textual representation"""
    try:
        return re.sub(r'<a[^>]+href\=(?:\"|\'|)([^\s\"\'\>]+)[^>]*>([^<]*)<\/a>', r'\2 (\1)', value, flags=re.IGNORECASE)
    except Exception:
        return value


@register.filter(is_safe=False)
@stringfilter
def imgs_to_text(value):
    """Extracts images from html for textual representation"""
    try:
        return re.sub(r'<img[^>]+src\=(?:\"|\'|)([^\s\"\'\>]+)[^>]*>', r'\1', value, flags=re.IGNORECASE)
    except Exception:
        return value


@register.filter(is_safe=False)
@stringfilter
def inline_style(value, arg=""):
    """Inlines CSS into HTML (for maillist templates)"""
    try:
        # arg в формате, например, "a color:#ccc;font-weight:bold"
        element, inline_style = arg.split(' ', 1)
        
        def replacer(m):
            el_str = m.group(1)
            el_str_to_search = el_str.lower()  # чтобы дважды не приводить строку ниже
            if 'style="' in el_str_to_search or 'style=\'' in el_str_to_search:
                return re.sub(
                    r'style=(\"|\')(.+?)(?:\"|\')',
                    r'style=\1\2;%s\1' % inline_style,
                    el_str, flags=re.I, count=1
                )
            else: # втыкаем аттрибут style
                return el_str.replace('>', ' style="%s">' % inline_style)
        
        return re.sub(r'(<'+re.escape(element)+r'[^>]*>)', replacer, value, flags=re.I)
    except Exception:
        return value

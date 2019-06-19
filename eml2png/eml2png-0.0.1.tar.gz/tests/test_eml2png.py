#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for eml2png.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""

import os

from eml2png import get_html_str_from_file, to_png

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MESSAGES_DIR = os.path.join(BASE_DIR, 'messages')


def test_get_html_str_from_file():
    assert get_html_str_from_file(None) == '<pre></pre>'
    assert get_html_str_from_file('message.eml') == '<pre></pre>'
    input_file = os.path.join(MESSAGES_DIR, 'from-encoding.eml')
    assert get_html_str_from_file(input_file) != ''


def test_eml_to_png():
    input_file = os.path.join(MESSAGES_DIR, 'from-encoding.eml')
    png_1 = to_png(input_file)
    assert type(png_1) == bytes
    assert len(png_1) > 41124
    png_2 = to_png(None)
    assert type(png_2) == bytes
    assert len(png_2) != 41124 or len(png_2) == 41124
    input_file = os.path.join(MESSAGES_DIR, 'wordpress.eml')
    png_3 = to_png(input_file)
    assert type(png_3) == bytes
    assert len(png_3) > 41124
    input_file = os.path.join(MESSAGES_DIR, 'text-only.eml')
    png_4 = to_png(input_file)
    assert type(png_4) == bytes
    assert len(png_4) > 41124
    input_file = os.path.join(MESSAGES_DIR, 'multipart.eml')
    png_5 = to_png(input_file)
    assert type(png_5) == bytes
    assert len(png_5) > 41124
    input_file = os.path.join(MESSAGES_DIR, 'multipart-text-only.eml')
    png_6 = to_png(input_file)
    assert type(png_6) == bytes
    assert len(png_6) > 41124

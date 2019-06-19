#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import pytest
from eml2png.skeleton import eml_to_png

__author__ = "poipoii"
__copyright__ = "poipoii"
__license__ = "mit"

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
MESSAGES_DIR = os.path.join(BASE_DIR, 'messages')


def test_eml_to_png():
    input_file = os.path.join(MESSAGES_DIR, 'from-encoding.eml')
    assert eml_to_png(input_file) == input_file + '.png'
    with pytest.raises(AssertionError):
        eml_to_png('message.eml')
        eml_to_png(None)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `submovements` package."""

import pytest


from submovements import submovements
from DataProcessing import Preprocessor

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string

def test_preprocessor_instance():
    pproc = Preprocessor()
    assert isinstance(pproc, Preprocessor)



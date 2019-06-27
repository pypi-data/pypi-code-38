#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `t2stimulate` package."""

import pytest

import numpy as np

from t2stimulate.simulate import stimulate
from t2stimulate.fit.fit import fit
from t2stimulate.fit.fit import Component


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


def test_t2stimulate_b1refocussing(response):
    # Basic Curve
    num_echoes = 64
    tau = 5
    component_initial = Component(985, 22, 900)

    curve = component_initial.pd * stimulate(alpha=160 / 180 * np.pi, num_echoes=num_echoes, T1=component_initial.t1,
                                             T2=component_initial.t2, tau=tau)

    curve_e = np.sqrt( (curve + np.random.normal(0, 5, num_echoes))**2 + np.random.normal(0, 5, num_echoes)**2)

    te = 2 * tau * np.arange(1, num_echoes + 1)

    components_initial = (component_initial,)
    b1_initial = 170 / 180 * np.pi

    x = fit(te, curve_e, components_initial, b1_initial)
    print(x, 160/180*np.pi)

    assert True

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `t2stimulate` package."""

import pytest

import numpy as np

from t2stimulate.simulate import stimulate


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
    curve = stimulate(alpha=np.pi, num_echoes=5, T1=1000, T2=80, tau=5)

    assert np.allclose(curve, np.array([0.8824969, 0.77880078, 0.68728928, 0.60653066, 0.53526143]))

    # Lower flip angle Curve
    curve = stimulate(alpha=170 / 180 * np.pi, num_echoes=5, T1=1000, T2=80, tau=5)

    assert np.allclose(curve, np.array([0.87579335, 0.78018687, 0.68201487, 0.60873607, 0.53107402]))

    # 90 degree refocussing flip angle
    curve = stimulate(alpha=90 / 180 * np.pi, num_echoes=5, T1=1000, T2=80, tau=5)

    assert np.allclose(curve, np.array([0.44124845, 0.63155815, 0.55734811, 0.47468203, 0.41890542]))


def test_t2stimulate_numechoes(response):
    result = np.array([0.85588636, 0.78364414, 0.6675115, 0.6131273, 0.52151495,
                       0.47890863, 0.40811059, 0.37358872, 0.31967318, 0.29129722,
                       0.25038159, 0.22727689, 0.19587117, 0.17762711, 0.15289925,
                       0.13915641, 0.11904341, 0.10929365, 0.09245346, 0.08601781,
                       0.07166901, 0.06778384, 0.05550148, 0.05343787, 0.04296809,
                       0.04212754, 0.03325952, 0.03321771, 0.02572334, 0.02622135,
                       0.01984966, 0.02075043])

    # Few echoes
    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=3, T1=1000, T2=80, tau=5)

    assert np.allclose(curve, result[:3])

    # Few echoes
    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=15, T1=1000, T2=80, tau=5)

    assert np.allclose(curve, result[:15])

    # 32 echoes
    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=32, T1=1000, T2=80, tau=5)

    assert np.allclose(curve, result)


def test_t2stimulate_t2(response):
    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=1000, T2=20, tau=5)

    assert np.allclose(curve, np.array([0.58824152, 0.38115041, 0.21238988, 0.14887362, 0.0732573,
                                        0.06113308, 0.02222788, 0.02757839, 0.0038753, 0.01443641]))

    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=1000, T2=80, tau=5)

    assert np.allclose(curve, np.array([0.85588636, 0.78364414, 0.6675115, 0.6131273, 0.52151495,
                                        0.47890863, 0.40811059, 0.37358872, 0.31967318, 0.29129722]))

    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=1000, T2=140, tau=5)

    assert np.allclose(curve, np.array([0.9029878, 0.86930194, 0.78420596, 0.75432046, 0.68227728,
                                        0.65352062, 0.59438338, 0.5656607, 0.51807706, 0.48957907]))

    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=1000, T2=300, tau=5)

    assert np.allclose(curve, np.array([0.93805097, 0.93594812, 0.87919668, 0.8744822, 0.8253415,
                                        0.81601533, 0.77550069, 0.76105825, 0.72872955, 0.71001549]))


def test_t2stimulate_t2(response):
    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=500, T2=40, tau=5)

    assert np.allclose(curve, np.array([0.75531707, 0.61515309, 0.45765074, 0.37871017, 0.27706674,
                                        0.23331114, 0.16756293, 0.14391496, 0.10110945, 0.08902654]))

    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=500, T2=150, tau=5)

    assert np.allclose(curve, np.array([0.907298, 0.87682296, 0.79552223, 0.7674361, 0.69872935,
                                        0.67070899, 0.61443793, 0.58571367, 0.54050228, 0.51152747]))

    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=1000, T2=40, tau=5)

    assert np.allclose(curve, np.array([0.75531707, 0.61560182, 0.45749782, 0.37940138, 0.27675072,
                                        0.23410671, 0.16712624, 0.14472953, 0.10059922, 0.08981685]))

    curve = stimulate(alpha=160 / 180 * np.pi, num_echoes=10, T1=1000, T2=150, tau=5)

    assert np.allclose(curve, np.array([0.907298, 0.87736198, 0.79550237, 0.76837305, 0.6987273,
                                        0.67188742, 0.61451089, 0.5869956, 0.54069289, 0.51281792]))

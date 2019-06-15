"""
This set of tests evaluates the `BaseLayer` class and those classes that
inherit from it.
"""

import pytest
import numpy as np
from armmwave import layer

@pytest.mark.parametrize('test_l, expected', [
    (layer.BaseLayer(), ['Basic layer', 1., 0., 1.]),
    (layer.Layer(), ['Basic layer', None, None, 1., 0., 1.]),
    (layer.Source(), ['Source layer', layer._Void(), 1., 0., np.inf]),
    (layer.Terminator(), ['Terminator layer', layer._Void(), 1., 0., np.inf, True]),
    ])
def test_default_class_attrs(test_l, expected):
    """
    Check that classes and subclasses are properly instantiated
    with sane default values.
    """
    test_attr = [test_l.__dict__[key] for key in sorted(test_l.__dict__.keys())]
    assert test_attr == expected 

def test_get_rind():
    """Check that we get the refractive index we expect."""
    test_l = layer.BaseLayer()
    assert test_l.get_rind() == 1.

def test_get_thick():
    """Check that we get the thickness we expect."""
    test_l = layer.BaseLayer()
    assert test_l.get_thick() == 1.

def test_get_tand():
    """Check that we get the loss tangent we expect."""
    test_l = layer.BaseLayer()
    assert test_l.get_tand() == 0.

def test_get_desc():
    """Check that we get the description we expect."""
    test_l = layer.BaseLayer()
    assert test_l.get_desc() == 'Basic layer'

@pytest.mark.parametrize('test_l, expected', [
    (layer.BaseLayer(), 'Basic layer (Basic layer)'),
    (layer.Layer(), 'Basic layer (Sim layer)'),
    (layer.Source(), 'Source layer (Source layer)'),
    (layer.Terminator(), 'Terminator layer (Terminator layer)'),
    (layer._Void(), 'There is nothing but THE VOID'),
    ])
def test_default_repr(test_l, expected):
    """Check that we get the string representation we expect."""
    assert repr(test_l) == expected

def test_not_a_void():
    """Check that we don't mistake a regular layer for The Void."""
    assert not (layer.Source() == layer._Void())

"""
Contains tests for the `Model` class, which ultimately act as an
integration test. The `run` method forces us to check whether all the
bits and pieces fit together. This is particularly important for the
two functions in `armm.core` that are difficult to test on their own.
"""
import os
import pytest
import numpy as np
import numpy.testing as npt
from armmwave import model
from armmwave import layer

TEST_DIR_LOC = 'test'
OUTPUT_LOC = os.path.join('{}'.format(TEST_DIR_LOC), 'pytest_armm_output')

def test_default_attr():
    """Check that we create `Model` class with expected attributes"""
    test_m = model.Model()
    model_attrs = [test_m.__dict__[key] for key in test_m.__dict__.keys()]
    expected = [None] * len(model_attrs)
    assert model_attrs == expected

@pytest.mark.parametrize('f1, f2, nsample, expected', [
    (0., 0., 0., 'error_condition'),
    (1., 0., 3, np.array([1., 0.5, 0.])),
    (0., 0., 1000, np.array([0])),
    (0., 1., 3, np.array([0., 0.5, 1.])),
    ])
def test_set_freq_range(f1, f2, nsample, expected):
    """Check that we can properly set the frequency sweep"""
    test_m = model.Model()
    if nsample == 0:
        pytest.raises(ValueError, test_m.set_freq_range, f1, f2, nsample)
        return
    test_m.set_freq_range(f1, f2, nsample)
    npt.assert_equal(test_m.freq_range, expected)

@pytest.mark.parametrize('f1, f2, expected_low, expected_high', [
    (1., 0., 0., 1.),
    (0., 1., 0., 1.),
    ])
def test_check_freq_bounds(f1, f2, expected_low, expected_high):
    """Check that we can properly set the high and low frequency bounds"""
    test_m = model.Model()
    test_m.set_freq_range(f1, f2)
    assert test_m.low_freq == expected_low
    assert test_m.high_freq == expected_high

def test_set_angle_range():
    """
    Check that we can properly set the angle sweep.

    This test should raise a NotImplementedError for now.
    """
    test_m = model.Model()
    pytest.raises(NotImplementedError, test_m.set_angle_range, 0, 0)

@pytest.mark.parametrize('test_layers, expected_rind', [
    ([layer.Source(), layer.Layer(rind=999), layer.Terminator(vac=True)], [1., 999., 1.]),
    ([layer.Source(), layer.Layer(rind=999), layer.Terminator(vac=False)], [1., 999., 999.]),
    ([layer.Source(), layer.Layer(rind=999), layer.Terminator(rind=333)], [1., 999., 333.]),
    ])
def test_set_up_basic(test_layers, expected_rind):
    """
    Check that we can run through `set_up` with the most basic default
    values.
    """
    test_m = model.Model()
    test_m.set_up(test_layers)
    assert test_m.rinds == expected_rind
    assert test_m.tands == [0., 0., 0.]
    assert test_m.thicks == [np.inf, 1., np.inf]
    assert test_m.low_freq == 500e6
    assert test_m.high_freq == 500e9
    assert test_m.pol == 's'
    assert test_m.incident_angle == 0.

def test_set_up_lt3_layers():
    """
    Ensure that we raise an IndexError in the event we try to build a
    model with fewer than three layers.
    """
    layers = [layer.Source(), layer.Terminator()]
    test_m = model.Model()
    pytest.raises(IndexError, test_m.set_up, layers)

def test_set_up_perpendicular_incidence():
    """
    Ensure that we raise an IndexError in the event we try to build a
    model with fewer than three layers.
    """
    layers = [layer.Source(), layer.Layer(), layer.Terminator()]
    test_m = model.Model()
    pytest.raises(ValueError, test_m.set_up, layers, 500e6, 500e9, np.pi/2, 's')

@pytest.mark.parametrize('test_layers', [
    ([layer.Layer(), layer.Layer(), layer.Terminator()]),
    ([layer.Source(), layer.Layer(), layer.Layer()]),
    ])
def test_set_up_bad_source_or_term(test_layers):
    """
    Ensure that we raise an IndexError in the event we try to build a
    model with fewer than three layers.
    """
    test_m = model.Model()
    pytest.raises(TypeError, test_m.set_up, test_layers)

def test_set_up_halpern_layer():
    """
    Check that we can set up a layer with Halpern coefficients, even if
    other layers aren't created with Halpern coefficients.
    """
    layers = [layer.Source(), layer.Layer(),
              layer.Layer(halperna=999., halpernb=111.),
              layer.Layer(), layer.Terminator()]
    test_m = model.Model()
    test_m.set_up(layers)
    assert list(test_m.halpern_layers.keys()) == [2]
    assert test_m.halpern_layers[2] == {'a' : 999., 'b' : 111., 'n' : 1.}

def test_reset_model():
    """
    Check that we can create a basic model, then return all of the model's
    attributes to their defaults.
    """
    layers = [layer.Source(), layer.Layer(), layer.Terminator()]
    test_m = model.Model()
    expected_attrs = [None] * len(test_m.__dict__.keys())
    test_m.set_up(layers)
    assert test_m.rinds == [1., 1., 1]
    assert test_m.tands == [0., 0., 0.]
    assert test_m.thicks == [np.inf, 1., np.inf]
    assert test_m.low_freq == 500e6
    assert test_m.high_freq == 500e9
    assert test_m.pol == 's'
    assert test_m.incident_angle == 0.
    test_m.reset_model()
    reset_attrs = [test_m.__dict__[key] for key in test_m.__dict__.keys()]
    assert reset_attrs == expected_attrs

def test_run_without_set_up():
    """
    Check that we raise a KeyError if we try to run a model without
    setting it up first.
    """
    test_m = model.Model()
    pytest.raises(KeyError, test_m.run)

def test_run():
    """
    Check that we can run the most basic model available---i.e., all
    default values.
    """
    layers = [layer.Source(), layer.Layer(), layer.Terminator()]
    test_m = model.Model()
    test_m.set_up(layers)
    results = test_m.run()
    npt.assert_allclose(results['transmission'], np.ones(results['transmission'].size))
    npt.assert_allclose(results['reflection'], np.zeros(results['reflection'].size))

def test_run_halpern():
    """
    Check that we can run the most basic model available, but with Halpern
    coefficients.
    """
    layers = [layer.Source(), layer.Layer(halperna=0., halpernb=0.), layer.Terminator()]
    test_m = model.Model()
    test_m.set_up(layers)
    results = test_m.run()
    npt.assert_allclose(results['transmission'], np.ones(results['transmission'].size))
    npt.assert_allclose(results['reflection'], np.zeros(results['reflection'].size))

def test_save():
    """
    Check that we can save the output of a model to a file
    """
    layers = [layer.Source(), layer.Layer(), layer.Terminator()]
    test_m = model.Model()
    test_m.set_up(layers)
    results = test_m.run()
    test_m.save(OUTPUT_LOC)
    dat = np.genfromtxt(OUTPUT_LOC, unpack=True)
    expected_fs = np.linspace(500e6, 500e9, num=1000)
    expected_ts = np.ones(1000)
    expected_rs = np.zeros(1000)
    assert dat.shape == (3, 1000)
    npt.assert_allclose(dat[0], expected_fs)
    npt.assert_allclose(dat[1], expected_ts)
    npt.assert_allclose(dat[2], expected_rs)
    os.remove(OUTPUT_LOC)

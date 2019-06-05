import os.path
import numpy as np
import pandas as pd
import astropy.units as u
try:
    from ..g_values import gValue, RadPresConst
except:
    from atomicdataMB import gValue, RadPresConst

def test_gValue():
    """Compare gvalues with gvalues in IDL code."""
    eps = 1e-5

    ## Test 1
    g = gValue('Na', 5891, 1.5)

    correct = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data',
                                       'g_value_test_data_Na_5891_1.5.dat'))
    newg = np.interp(g.velocity.value, correct.velocity, correct.g)

    assert g.wavelength == 5891.*u.AA
    assert g.species == 'Na'
    assert g.aplanet == 1.5*u.au
    assert np.all(np.abs(g.g.value - newg < eps))

    ## Test 2
    g = gValue('Na', 5891*u.AA, 1.5)

    correct = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data',
                                       'g_value_test_data_Na_5891_1.5.dat'))
    newg = np.interp(g.velocity.value, correct.velocity, correct.g)

    assert g.wavelength == 5891.*u.AA
    assert g.species == 'Na'
    assert g.aplanet == 1.5*u.au
    assert np.all(np.abs(g.g.value - newg < eps))

    ## Test 3
    g = gValue('Na', 5891, 1.5*u.au)

    correct = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data',
                                       'g_value_test_data_Na_5891_1.5.dat'))
    newg = np.interp(g.velocity.value, correct.velocity, correct.g)

    assert g.wavelength == 5891.*u.AA
    assert g.species == 'Na'
    assert g.aplanet == 1.5*u.au
    assert np.all(np.abs(g.g.value - newg < eps))

def test_radpresconst():
    """Compare gvalues with gvalues in IDL code."""
    eps = 1e-5
    const = RadPresConst('Na', 1.5)

    correct = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data',
                                       'g_value_test_data_Na_5891_1.5.dat'))

    newconst = np.interp(const.velocity.value, correct.velocity,
                         correct.radaccel)

    assert const.species == 'Na'
    assert const.aplanet == 1.5*u.au
    assert np.all(np.abs(const.accel.value - newconst) < eps)

if __name__ == '__main__':
    test_gValue()
    test_radpresconst()

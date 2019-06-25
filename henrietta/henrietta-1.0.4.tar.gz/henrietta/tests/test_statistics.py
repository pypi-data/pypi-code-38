from ..statistics import *

def test_photons():
    '''
    This function tests the toy photon light curve.
    '''

    lc = create_photon_lightcurve()
    lc.plot(marker='.', linewidth=0)

def test_bucket():
    '''
    This function tests the catch_photons_in_bucket function.
    '''
    N = catch_photons_in_bucket(rate=1, time=2, diameter=3, visualize=False)
    print(N)

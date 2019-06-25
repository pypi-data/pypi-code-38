from henrietta.photometry import *
import numpy as np
import matplotlib.pyplot as plt
import illumination as il

def test_photometry():
    ax = plt.subplot(111)
    im = create_test_array(N=1, xsize=100, ysize=100, nstars=10, single=False,seed=7)
    test = mean_centroid(im,[50,50],boxsize=60.,num_stars=1)
    print test
    return test

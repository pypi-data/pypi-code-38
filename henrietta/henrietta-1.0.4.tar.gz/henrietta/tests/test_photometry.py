from henrietta.photometry import *
import numpy as np
import matplotlib.pyplot as plt
import illumination as il

def test_photometry():
    ax = plt.subplot(111)
    im = create_test_array(N=1, xsize=100, ysize=100, nstars=10, single=False,seed=7)
    test = photometry(ax,im[0],[[54,91],[44,38]],ap_size=3,r_in=8,r_out=12,back_photo=True)
    return test

if __name__ == '__main__':
    test_photometry()

#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np
from scipy.fftpack import fftfreq, rfft

__all__ = ['fft_calculator']

def fft_calculator(xVals, yVals, collectRate):
    """Calculate the FFT of the given arrays.

    Parameters
    ----------
    xVals : numpy.array
        The x coordinates of the centroids.
    yVals : numpy.array
        The y coordinates of the centroids.
    collectRate : float
        The rate at which the data was collected (FPS).

    Returns
    -------
    (numpy.array, numpy.array, numpy.array)
        The FFTX, FFTY and Frequency arrays on the positive Frequency portion.
    """
    # Assume both arrays are same length.
    arrayLen = xVals.size

    xMean = np.mean(xVals)
    yMean = np.mean(yVals)

    xFft = rfft(xVals - xMean)
    yFft = rfft(yVals - yMean)

    frequencies = fftfreq(arrayLen, 1 / collectRate)

    dslice = slice(1, arrayLen // 2)

    return xFft[dslice], yFft[dslice], frequencies[dslice]

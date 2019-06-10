""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 02/11/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : FourierPeriodogram

History : (02/11/2016) First version.

"""

import numpy as np


def FourierPeriodogram(t, y, minf=None, maxf=None):
    N = len(t)
    step = t[1] - t[0]
    frequency = np.fft.fftfreq(N, step)
    y_fft = np.fft.fft(y)
    if minf != None and maxf != None:
        positive = ((frequency > 0) & (frequency >= minf) & (frequency <= maxf))
    else:
        positive = (frequency > 0)
    return frequency[positive], (1./N) * abs(y_fft[positive]) ** 2


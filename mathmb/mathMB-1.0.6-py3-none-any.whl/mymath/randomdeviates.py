'''Compute random deviates from arbitrary 1D and 2D distributions.'''

import numpy as np
import numpy.random as random
from scipy import interpolate


def random_deviates_1d(x, f_x, num):
    '''Compute random deviates from arbitrary 1D distribution.

    Uses Transformation method (Numerical Recepies, 7.3.2)
    '''

    cumsum = f_x.cumsum()
    cumsum -= cumsum.min()
    cumsum /= cumsum.max()
    return np.interp(random.rand(num), cumsum, x)

def random_deviates_2d(fdist, x0, y0, num):
    '''Compute random deviates from arbitrary 2D distribution.

    Uses acceptance/rejection method.
    Inputs:
        fdist: 2d array of relative probability
        x0: xaxis
        y0: yaxis
        num: number of points to choose
    outputs:
        x, y: vectors of length num
    '''

    mx = (x0.max()-x0.min(), x0.min())
    my = (y0.max()-y0.min(), y0.min())
    fmax = fdist.max()

    xpts, ypts = [], []
    while len(xpts) < num:
        ux = random.rand(num)*mx[0] + mx[1]
        uy = random.rand(num)*my[0] + my[1]
        uf = random.rand(num)*fmax

        val = interpolate.interpn((x0, y0), fdist, (ux, uy))
        mm = uf < val
        xpts.extend(list(ux[mm]))
        ypts.extend(list(uy[mm]))

    xpts, ypts = xpts[0:num], ypts[0:num]
    un = xpts[0].unit
    xpts = np.array([i.value for i in xpts])*un
    un = ypts[0].unit
    ypts = np.array([i.value for i in ypts])*un
    return xpts, ypts

# def RandomGaussian(mu, sigma, num):
#     '''Choose random deviates from a 1D normal distribution.
#     mu = mean value
#     sigma = FWHM
#     num = number of particles
#     '''
#
#     u0, u1 = random.rand(num), random.rand(num)
#     ypr = np.sin(2*np.pi*u0) * np.sqrt(-2*np.log2(u1))
#     y = sigma * ypr + mu
#     return y

def random_gaussian(mu, sigma, num):
    '''Choose random deviates from a 1D normal distribution.

    Uses np.random.randn. This is faster than RandomGaussian
    mu = mean value
    sigma = FWHM
    num = number of particles
    '''

    return random.randn(num)*sigma*np.sqrt(2*np.log(2)) + mu


if __name__ == '__main__':
    test1 = False
    test2 = True

    if test1:
        x = np.arange(101)
        y = np.sin(x/100*2*np.pi)**2

        rr = RandomDeviates1d(x, y, 1000000)
        hh, xx = np.histogram(rr, bins=101)

        plt.plot(x, y/y.max())
        plt.plot((xx[:-1]+xx[1:])/2., hh/hh.max())
        plt.show()

    if test2:
        f0 = RandomGaussian(3., 0.5, 1000000)
        f1 = RandomGaussian2(3., 0.5, 1000000)
        f2 = random.randn(1000000)*0.5*np.sqrt(2*np.log(2)) + 3

        h0, x0 = np.histogram(f0, bins=100, range=(0,6))
        h1, x1 = np.histogram(f1, bins=100, range=(0,6))
        h2, x2 = np.histogram(f2, bins=100, range=(0,6))

        x0 = (x0[0:-1]+x0[1:])/2.
        x1 = (x1[0:-1]+x1[1:])/2.
        x2 = (x2[0:-1]+x2[1:])/2.

        plt.plot(x0, h0)
        plt.plot(x1, h1)
        plt.plot(x2, h2)
        plt.show()

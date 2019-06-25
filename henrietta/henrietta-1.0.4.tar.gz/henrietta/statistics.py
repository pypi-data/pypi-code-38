import numpy as np, matplotlib.pyplot as plt
from lightkurve import LightCurve
plt.ion()

def create_photon_lightcurve(N=100, cadence=0.5/24.0, duration=1):
    '''
    Create a lightkurve object, assuming we detect
    a particular number of photons per exposure.

    Parameters
    ----------

    N: float
        The average number of photons per exposure.
    cadence: float
        The time between successive exposures (in days).
    duration: float
        The total time spanned by the light curve (in days).
    '''
    t = np.arange(0, duration, step=cadence)
    photons = np.random.poisson(N, t.shape)
    lc = LightCurve(time=t,
                    flux=photons,
                    flux_err=np.sqrt(photons),
                    meta=dict(name='Poisson light curve with {} photons/s'.format(N)))
    return lc

def create_approximate_lightcurve(N=100, cadence=0.5/24.0, duration=1):
    '''
    Create a lightkurve object, assuming we detect
    a particular number of photons per exposure,
    but treating the PDF for photon counts with the
    Gaussian approximation, instead of a true Poisson
    distribution.

    Parameters
    ----------

    N: float
        The average number of photons per exposure.
    cadence: float
        The time between successive exposures (in days).
    duration: float
        The total time spanned by the light curve (in days).
    '''
    t = np.arange(0, duration, step=cadence)
    photons = np.random.normal(N, np.sqrt(N), t.shape)
    lc = LightCurve(time=t,
                    flux=photons,
                    flux_err=np.sqrt(photons),
                    meta=dict(name='Poisson light curve with {} photons/s'.format(N)))
    return lc

def catch_photons_in_bucket(rate=1, diameter=1.0, time=60*30.0, visualize=True):
    '''
    Simulate a telescope catching photons,
    for a given photon flux (photons/s/m**2),
    telescope diameter (m), and exposure time (s).

    Parameters
    ----------
    rate: float
        The rate at which photons are coming towards us,
        expressed in units of (photons/s/m**2).

    diameter: float
        The effective diameter of a circular telescope,
        expressed in units of (m).

    time: float
        The exposure duration, expressed in units of (s).

    Returns
    -------
    N: int
        The number of photons that land in the telescope
    '''

    # what's the radius of the telescope
    radius = diameter/2.0

    if visualize:

        # make a rectangle that at least include the telescope
        square = np.maximum(1.3*diameter, 1.0)

        # what's the expected total number of photons
        area = square*square

        # create a rectangle of randomly located photons
        Ntotal = np.random.poisson(area*time*rate)
        x, y = np.random.uniform(-square/2, square/2, (2, Ntotal))

        # determine which of these photons landed in the telescope
        incircle = (x**2 + y**2) < radius**2
        outofcircle = ~incircle
        N = np.sum(incircle)

        kw = dict(marker='.', markeredgecolor='none', alpha=0.5, linewidth=0)
        plt.figure(figsize=(4,4))
        plt.plot(x[incircle], y[incircle], color='mediumseagreen', **kw)
        plt.plot(x[outofcircle], y[outofcircle], color='black', **kw)

        # draw a circle
        theta = np.linspace(0, 2*np.pi, 1000)
        plt.plot(radius*np.sin(theta), radius*np.cos(theta), linewidth=4, color='black')

        # label the radius of the circle
        plt.text(0, -radius*1.1, '{}m'.format(diameter), ha='center', va='top', fontweight='bold', fontsize=10, color='mediumseagreen')

        # add a title
        plt.title('{} photons gathered in {}s\n({} photons/s/m$^2$)'.format(N, time, rate))

        # set the aspect ratio of the plot to 1:1
        plt.axis('equal')
        plt.xlim(-square/2, square/2)
        plt.ylim(-square/2, square/2)

        # get rid of the square around the plot
        plt.axis('off')
        plt.subplots_adjust(top=0.8)
        plt.show()

    else:

        # if we don't need to make plot, just draw a Poisson number
        area = np.pi*radius**2
        N = np.random.poisson(area*time*rate)

    return N

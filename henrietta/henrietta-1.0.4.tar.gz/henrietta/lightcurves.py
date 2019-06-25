from lightkurve import KeplerLightCurveFile, lightcurve, search_lightcurvefile
import matplotlib.pyplot as plt
import numpy as np
from .tools import *
from lightkurve.lightcurve import LightCurve
from lightkurve.collections import LightCurveFileCollection


def download_kepler_lc(star='Kepler-186',
                       quality_bitmask='hard',
                       kind='PDCSAP_FLUX', **kw):
    '''
    This function is a wrapper to download one or more quarters of Kepler
    lightcurve data, and extract a LightCurve object from it.

    When downloading a Kepler LightCurveFile from online, we get lots
    of information, including multiple different kinds of light curves
    for the same star. The goal of this little wrapper is to make it
    easy to get just one single light curve to play with.

    This has been tested only on data from the main Kepler mission.
    For K2 data, you may need to download a TPF.

    Parameters
    ----------

    star: str, int
        The name of the star whose light curve you want to download.
        This can be a name ("Kepler-42", "KOI-961") or a KIC number
        (8561063)

    quarter: str, int
        Which Kepler quarter to download?
            'all' = download the entire mission of data
            1, 2, 3 ... = download a specific quarter

    cadence: str
        'long' for Kepler long cadence
        'short' for Kepler short cadence

    quality_bitmask: str, int
        'none' = ignore no data
        'default' = ignore data with serious quality issues
        'hard' = be a little more cautious in what we call good data
        'hardest' = be too cautious about what we call good data

    kind: str
        "SAP_FLUX" = simple aperture photometry
        "PDCSAP_FLUX" = SAP, with pre-search data conditioning applied to get
        rid of some instrumental systematics from the light curves (but watch
        out! some astrophysical signals might be messed up too!)

    kw : dict
        Additional keywords will be passed to `.from_archive`.

    Returns
    -------

    lc: LightCurve object
        This is a `lightkurve`-style LightCurve object, which contains
        the attributes `lc.time` (times in JD) and `lc.flux` (the brightness
        of the star), as well as lots of methods for analysis and plotting.

    '''

    # download a KeplerLightCurveFile (or list of them) from the MAST archive
    lcf = search_lightcurvefile(star,**kw).download_all(quality_bitmask=quality_bitmask)

    # if a list, stitch things together (crudely! will be terrible for SAP!)
    if isinstance(lcf, LightCurveFileCollection):

        # make a normalized light curve from the first light curve file
        lc = lcf[0].get_lightcurve(kind).normalize()

        # append the normalized light curves from all other light curve files
        for f in lcf[1:]:
            thisquarter = f.get_lightcurve(kind)
            lc = lc.append(thisquarter.normalize())

    # if a single quarter, simply return that light curve
    else:
        lc = lcf.get_lightcurve(kind)

    # return the light curve
    return lc

def download_lc(*args, **kwargs):
    return download_kepler_lc(*args, **kwargs)


def locate_transits(lc, period, t0=0, name=None, color='green', **kw):

    '''

    This function takes in a lightcurve object along with the planet's
    period and epoch in order to identify on the plot each expected location
    of a transit

    lc should be a lightkurve object which has times and fluxes.
    period should be in days
    t0 should be in BJD
    '''

    # pull out time and flux arrays
    time = lc.time
    flux = lc.flux

    # figure out the right time format
    if isinstance(lc, lightcurve.FoldedLightCurve):
        epoch = 0.0
        period = 1.0
    else:
        if lc.time_format == 'bkjd':
            epoch = bjd2bkjd(t0)
        elif lc.time_format == 'btjd':
            epoch = bjd2btjd(t0)
        else:
            epoch = t0

    # calculate the integer orbit numbers, and mid-transit locations
    allorbitnumbers = np.round((lc.time - epoch)/period).astype(np.int)
    n = np.arange(np.min(allorbitnumbers), np.max(allorbitnumbers))
    transit_loc = n*period + epoch

    #avg_flux = np.median(flux)
    #fig,ax = plt.subplots()
    #plt.title('Transit locations')
    #plt.xlabel('Time (JD)')
    #lt.ylabel('Flux')
    #plt.xlim(time[0],time[-1])
    #plt.scatter(time,flux)

    for i, this_transit in enumerate(transit_loc):
        if i == 0:
            label=name or '{period}{multiply}n + {epoch:.5f}'.format(multiply=r'$\times$', **locals())
        else:
            label=None
        plt.axvline(this_transit, ymin=0.9, ymax=0.95, alpha=0.4, color=color, label=label, **kw)
    return transit_loc


def extract_transits(lc, period, epoch, window=0.05):
    '''
    This function splits a light curve into two complementary
    light curves: one that includes just the transits (and a
    bit of a window surrounding them) and one that contains all
    the other non-transit parts of the light curve.

    Parameters
    ----------

    lc: object
        The 'lightkurve' object which contains transit data (time, flux) that
        we are analyzing.

    period: float
        The period (days) of the planet's orbit.

    epoch: float
        The JD value reported for the mid-transit time of this planet. Epoch
        is used to find other transits in the data.

    window: float
        The transit duration (in days), used here to specify a window of data
        points to extract as the in-transit data.

    Returns
    -------

    transits: LightCurve object
        This is a `lightkurve`-style LightCurve object, which contains
        the attributes `lc.time` (times in JD) and `lc.flux` (the brightness
        of the star). This object contains the data points between ingress
        egress of a transit.

    notransits: LightCurve object
        This is a `lightkurve`-style LightCurve object, which contains
        the attributes `lc.time` (times in JD) and `lc.flux` (the brightness
        of the star). This object contains the data points outside of a transit.

    '''

    time = lc.time
    flux = lc.flux
    error = lc.flux_err

    n = np.round((time-epoch)/period)
    n_transit = np.unique(n)

    mid_transit_times = (period*n_transit + epoch)

    ingress = []
    egress = []

    for i in range(len(n_transit)):
        if (mid_transit_times[i] >= lc.time[0]):
            if (mid_transit_times[i] <= lc.time[-1]):

                t0 = mid_transit_times[i]
                ingress.append(t0 - window/2.0)
                egress.append(t0 + window/2.0)

    transit_indices = []

    for i in range(len(time)):
        for j in range(len(ingress)):
            if time[i] >= ingress[j]:
                if time[i] <= egress[j]:
                    transit_indices.append(i)

    transit_time = time[transit_indices]
    transit_flux = flux[transit_indices]
    transit_error = error[transit_indices]

    oot_time = np.delete(time,transit_indices)
    oot_flux = np.delete(flux,transit_indices)
    oot_error = np.delete(error,transit_indices)

    transits = LightCurve(transit_time, transit_flux, transit_error)
    notransits = LightCurve(oot_time, oot_flux, oot_error)

    return transits, notransits

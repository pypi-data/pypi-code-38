from ..lightcurves import *
from ..modeling import *

def test_download_kepler_lc():
    '''
    This function tests the wrapper for downloading
    a single quarter of Kepler data.
    '''

    lc = download_kepler_lc('Kepler-17')
    ax = lc.plot(marker='.', linewidth=0)
    singlequarter = download_kepler_lc('Kepler-17', quarter=1)
    singlequarter.plot(ax=ax, marker='.', linewidth=0)


    folded = lc.fold(1.48571092)
    folded.scatter(marker='.', linewidth=0)

def test_locate():
    '''
    This function should draw a single circle
    around every transit in the Kepler-17 light curve.
    '''

    # download a Kepler-17 light curve
    lc = download_kepler_lc('Kepler-10', quarter=1)

    # make a light curve plot
    lc.flatten().plot(marker='.', linewidth=0)

    # draw lines for the planet on top
    locations = locate_transits(lc, period=0.837491, t0=2454964.57513, color='royalblue', name='Kepler-10b')
    locations = locate_transits(lc, period=45.294301, t0=2455062.26648, color='darkorange', name='Kepler-10c')

    plt.legend(bbox_to_anchor=(1,1), loc='upper left')
    plt.tight_layout()

def test_extract(period = 1.234, t0 = 2451234.5678, window = 0.05):

    # create a simulated light curve
    lc = simulate_transit_data(period=period, t0=t0)

    # split into two light curves, one with transits, one without
    transits, notransits = extract_transits(lc, period, epoch=t0, window=window)

    # make sure the sizes of these light curves make sense
    assert(len(transits.flux) + len(notransits.flux) == len(lc.flux))

    # make sure we can plot both of them (and)
    ax = transits.scatter(c='gray',normalize=False)
    notransits.scatter(ax=ax, c='darkorange',normalize=False)

    return transits, notransits

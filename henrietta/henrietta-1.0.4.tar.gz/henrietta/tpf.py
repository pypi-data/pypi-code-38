from lightkurve import KeplerTargetPixelFile, TessTargetPixelFile, search_targetpixelfile
from .imports import *
from .tools import *

def download_kepler_tpf(star='Kepler-186',
                        quarter=1,
                        cadence='long',
                        **kw):
    '''
    This function is a wrapper to download one or more "Target Pixel Files" (TPF)
    of Kepler data. Each TPF is basically a movie; it contains a time series
    of images in a tiny little area around a particular Kepler target.

    This has been tested only on data from the main Kepler mission and K2.

    Parameters
    ----------

    star: str, int
        The name of the star whose light curve you want to download.
        This can be a name ("Kepler-42", "KOI-961") or a KIC number
        (8561063)

    quarter: str, int
        Which Kepler quarter to download?
            1, 2, 3 ... = download a specific quarter

    cadence: str
        'long' for Kepler long cadence
        'short' for Kepler short cadence

    Returns
    -------

    tpf: KeplerTargetPixelFile object
        This is a `lightkurve`-style TargetPixelFile object, which contains
        the attributes `tpf.time` (times in JD) and `tpf.flux` (the brightness
        of each pixel as a function of time), as well as lots of methods for
        analysis and plotting.
    '''

    # download a KeplerLightCurveFile from the MAST archive
    tpf = search_targetpixelfile(star,
                                 quarter=quarter,
                                 cadence=cadence,
                                 **kw).download()
    return tpf

def download_k2_tpf(star='WASP-47', **kw):
    '''
    This function is a wrapper a "Target Pixel Files" (TPF) for Kepler/K2 data.
    Each TPF is basically a movie; it contains a time series of images in a tiny
    little area around a particular Kepler/K2 target.

    This has been tested only on data from the main Kepler mission and K2.

    Parameters
    ----------

    star: str, int
        The name of the star whose light curve you want to download.
        This can be a name ("K2-18", "TRAPPIST-1") or an EPIC number
        (246199087).

    Returns
    -------

    tpf: KeplerTargetPixelFile object
        This is a `lightkurve`-style TargetPixelFile object, which contains
        the attributes `tpf.time` (times in JD) and `tpf.flux` (the brightness
        of each pixel as a function of time), as well as lots of methods for
        analysis and plotting.
    '''

    # download a KeplerLightCurveFile from the MAST archive
    tpf = search_targetpixelfile(star, **kw).download()
    return tpf

def download_tess_tpf(star=261136679, **kw):
    '''
    This function is a wrapper a "Target Pixel Files" (TPF) for TESS data, as
    accessed through the MAST archive. Each TPF is basically a movie; it
    contains a time series of images in a tiny little area around a
    particular TESS target.

    This has been tested only on data from TESS Sector 1. The available
    data are described here:

    https://archive.stsci.edu/prepds/tess-data-alerts/

    Parameters
    ----------

    star: str, int
        The TESS Input Catalog ID of the star whose light curve
        you want to download. (We should make a more flexible interface
        for this in the future, once more data are available).

    Returns
    -------

    tpf: TessTargetPixelFile object
        This is a `lightkurve`-style TargetPixelFile object, which contains
        the attributes `tpf.time` (times in JD) and `tpf.flux` (the brightness
        of each pixel as a function of time), as well as lots of methods for
        analysis and plotting.
    '''

    # download a TessTargetPixelFile from the MAST archive
    url = "https://archive.stsci.edu/hlsps/tess-data-alerts/hlsp_tess-data-alerts_tess_phot_{:011}-s01_tess_v1_tp.fits".format(int(star))
    tpf = TessTargetPixelFile(url, **kw)

    # return the tpf
    return tpf

tpf = ()

import thefriendlystars as tfs
import astropy.units as u
from ..imports import *

def simulate_optics(target='Kepler-42', collectingarea=1.0, pixelscale=21.0, fov=3*60, background=0.0, **kw):
    '''

    Parameters
    ----------
    collectingarea : float
        The collecting area of the telescope, in units square meters.

    pixelscale : float
        The pixel scale, in units of arcseconds/pixel.

    fov : float
        The field-of-view of the telescope, in arcseconds.

    background : float
        What is the diffuse sky brightness,
        in units of photons/s/arcsecond**2?

    Returns
    -------
    flux_image : np.ndarray
        An image of the flux that would hit a detector,
        in units of photons/s/pixel. It is a *perfect*
        image, in the sense that no noise has been
        added to it.
    '''

    center = tfs.parse_center(target)

    catalog = tfs.Gaia.from_cone(center, radius=fov*u.arcsec/np.sqrt(2))
    # figure out the relative positions of the stars
    dra = ((catalog.ra - center.ra)*np.cos(center.dec)).to('arcsec').value
    ddec = (catalog.dec - center.dec).to('arcsec').value
    sx, sy = dra/pixelscale, ddec/pixelscale

    magnitudes = catalog.magnitude

    # (very approximate!)
    # 0 mag = 10^6 photons/s/cm^2
    # 0 mag = 10^10 photons/s/m^2
    zero = 1.0e6*(100)**2
    photonfluxes = zero*10**(-0.4*magnitudes)

    xsize = int(np.ceil(fov/pixelscale/2.0))
    ysize = xsize

    # create 2D arrays
    x1d = np.arange(-xsize, xsize)
    y1d = np.arange(-ysize, ysize)
    x, y = np.meshgrid(x1d, y1d)
    stars = np.zeros_like(x)

    # define the cartoon PSF for the stars
    sigma = 1.0

    def gauss(x, y, x0, y0):
        return 1.0/2*np.pi/sigma**2*np.exp(-0.5 * ((x - x0)**2 + (y - y0)**2) / sigma**2)

    # create a cube with an image for each star, and sum them together into one image
    stars = (photonfluxes * gauss(x[:, :, np.newaxis],
                                  y[:, :, np.newaxis],
                                  x0=sx, y0=sy)).sum(2)

    # create a model images
    model = (background + stars)#[np.newaxis, :, :] * np.ones(N).reshape((N, 1, 1))

    if type(model) == np.ma.core.MaskedArray:
        model = model.data
    return model*collectingarea

def simulate_detector(image, exptime=1.0, quantumefficiency=1.0, readnoise=10.0, **kw):
    '''
    Create a simulate image indicating the total number of
    photons that a detector will record per pixel, in a
    given exposure time.

    Parameters
    ----------
    image : np.ndarray
        An example flux image, in units of photons/s.
        For example, the output of `simulate_optics`
        would be a great input here!

    exptime : float
        The total exposure time, in units of seconds.
        How long do we let the detector collect photons
        before reading out the detector.

    quantumefficiency : float
        What fraction of incoming photons actually gets
        recorded as photons?
            1.0 is a perfect detector.
            0.0 is no detector at all.

    readnoise : float
        How much noise does the detector add to each pixel
        when it is read out of the detector? This is effectively
        in units of photons/pixel/exposure.

    Returns
    -------
    photon_image : np.ndarray
        An image of the total number of photons that
        would be recorded by the detector, in units of
        photons/pixel. It is a *noisy* image, in the sense
        it is a single realization of the image, and it
        will change if you run the function again.
    '''

    # calculate the expected total number of photons/pixel
    expectation = image*exptime*quantumefficiency

    # calculate a noise image, assuming Gaussian statistics
    noise = np.sqrt(expectation + readnoise**2)

    return np.random.normal(expectation, noise)

def simulate_image(*args, **kwargs):
    '''
    Make an end-to-end simulation of an astronomical image,
    combining the steps of `simulate_optics` with `simulate_detector`.

    Parameters
    ----------
        (anything that can be fed into `simulate_optics` or `simulate_detector`)

    Returns
    -------
    sim : array
        A simulated image.
    '''
    optics = simulate_optics(*args, **kwargs)
    exposure = simulate_detector(optics, **kwargs)
    return exposure

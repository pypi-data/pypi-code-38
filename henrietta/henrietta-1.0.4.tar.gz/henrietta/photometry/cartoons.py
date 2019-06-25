import numpy as np, matplotlib.pyplot as plt
from tqdm import tqdm

def create_test_array(N=5,
                      xsize=100,
                      ysize=100,
                      nstars=None,
                      single=False,
                      drift=0.0,
                      seed=None):
    '''
    Create a fake stack of images of stars
    (no cosmics injected, no jitter, Gaussian PDF).

    Parameters:
    -----------
    N : int
        The number of images.
    xsize : int
        The number of columns.
    ysize : int
        The number of rows.
    nstars : int
        The number of stars to include (defaults to be \propto to image area)
    single : bool
        Should this be just a single star in the center, or should it be many?
    drift : float
        The distance stars will drift per image, in pixels.

    Returns
    -------
    image_stack : array
        a simulated image of stars, with shape (N, ysize, xsize)
    '''

    # seed the random number generator (if None, will be truly random)
    np.random.seed(seed)

    # create images of x, y, and an empty one to fill with stars
    x1d = np.arange(0, xsize)
    y1d = np.arange(0, ysize)
    x, y = np.meshgrid(x1d, y1d)
    stars = np.zeros_like(x)

    # create N random position for stars
    if single:
        nstars = 1
        sx = np.atleast1d(np.random.normal(xsize / 2.0, 1))
        sy = np.atleast1d(np.random.normal(ysize / 2.0, 1))
    else:
        if nstars is None:
            nstars = np.minimum(int(xsize * ysize / 4), 1000)
        sx = np.random.uniform(0, xsize, nstars)
        sy = np.random.uniform(0, ysize, nstars)

    # set some background level
    bg = 30

    # create a semi-reasonable magnitude distribution for stars
    if single:
        topmag = 5
    else:
        topmag = 10

    # create fluxes for the star(s)
    sf = 10000 * 10**(-0.4 * np.random.triangular(0, topmag, topmag, nstars))

    # define the cartoon PSF for the stars
    sigma = 1.0

    # define a simple 2D Gaussian to represent the stars
    def gauss(x, y, x0, y0):
        return np.exp(-0.5 * ((x - x0)**2 + (y - y0)**2) / sigma**2)

    # either calculate one image at a time (with drift)
    if drift != 0.0:

        # create a stack of empty model images
        model = np.ones([N, ysize, xsize])

        # define some random direction in which stars will (linearly) drift
        theta = np.random.uniform(0, 2*np.pi)

        # loop over the images
        for i in tqdm(range(N)):
            # make up a nudge for this
            xnudge, ynudge = np.cos(theta) * i * drift, np.sin(theta) * i * drift

            # calculate a single fixed image of perfect (Gaussian) stars (at this nudge)
            stars = (sf * gauss(x[:, :, np.newaxis],
                                y[:, :, np.newaxis],
                                x0=sx + xnudge, y0=sy + ynudge)).sum(2)

            model[i, :, :] =  bg + stars
    # or calculate all the images at once
    else:
        # calculate a single fixed image of perfect (Gaussian) stars
        stars = (sf * gauss(x[:, :, np.newaxis],
                            y[:, :, np.newaxis],
                            x0=sx, y0=sy)).sum(2)

        # reshape that model into a cube
        model = (bg + stars)[np.newaxis, :, :] * np.ones(N).reshape((N, 1, 1))

    # add some Poisson noise to the cube of image
    image = np.random.normal(model, np.sqrt(model))

    return image

from ..imports import *
from .io import compile_rgb
import illumination as il
import astropy.units as u

def animate_tpf(tpf, showdifference=False, howmanydays=None, timestep=30):
    '''
    Create a .mp4 animation of the data in a TPF.

    Parameters
    ----------
    tpf : KeplerTargetPixelFile
        A time series of pixels.

    showdifference : bool
        Should we also show the difference image, of each frame
        with the median-frame subtracted?

    howmanydays : float
        The maximum number of days to animate.

    timestep : float
        The cadence at which to animate the movie, in units of minutes.
    '''

    # create a sequence of images
    seq = il.make_image_sequence(tpf.flux, time=tpf.time)

    # create a frame of the raw data
    frame = il.imshowFrame(data=seq, title='{} | {}'.format(tpf.mission, tpf.targetid))
    frames = [frame]


    if showdifference:
        # create a frame with the subtracted data
        diff = il.imshowFrame(data=seq, title='difference', processingsteps=['subtractmedian'])
        frames.append(diff)

    # create an illustration
    illustration = il.GenericIllustration(imshows=frames, sharecolorbar=False)
    filename = '{}-{}-animated.mp4'.format(tpf.mission, tpf.targetid)
    if howmanydays is None:
        maxtimespan = None
    else:
        maxtimespan = howmanydays*u.day
    if timestep is None:
        cadence = seq.cadence()
    else:
        cadence = timestep*u.minute
    illustration.animate(filename=filename, cadence=cadence, maxtimespan=maxtimespan)


def display_rgb(red=None, green=None, blue=None, size = 8, origin='upper'):
    '''
    Make a pediagogical plot showing how monochromatic red, green, and blue
    images can be combined to make a single color image.

    Parameters
    ----------
    red : 2D numpy array
        An image of the "red" brightness.
    green : 2D numpy array
        An image of the "green" brightness.
    blue : 2D numpy array
        An image of the "blue" brightness.
    '''

    # make sure that at least one of the images is defined
    if red is not None:
        anyimage = red
    elif green is not None:
        anyimage = green
    elif blue is not None:
        anyimage = blue
    assert(anyimage is not None)

    # replace undefined images with zeros
    if red is None:
        red = np.zeros_like(anyimage)
    if green is None:
        green = np.zeros_like(anyimage)
    if blue is None:
        blue = np.zeros_like(anyimage)

    # make sure the shapes of the images are consistent with each other
    assert(red.shape == green.shape)
    assert(blue.shape == green.shape)

    # set up the geometry for the figure
    aspectratio = red.shape[1]/float(red.shape[0])

    if aspectratio <= 1.0:
        figsize = (size*aspectratio, 5.0/3.0*size)
    else:
        figsize = (size, 5.0/3.0*size/aspectratio)
    plt.figure(figsize=figsize)

    # set up a grid of axes
    gs = plt.matplotlib.gridspec.GridSpec(3, 3, height_ratios=[1, 1, 3], wspace=0.01, hspace=0.01, left=0.1, right=0.9, bottom=0.05, top=0.9)
    ax = {}
    ax['color'] = plt.subplot(gs[2,:])

    colors = ['red', 'green', 'blue']
    for i, k in enumerate(colors):
        ax[k+'-gray'] = plt.subplot(gs[0,i], sharex=ax['color'], sharey=ax['color'])
        ax[k+'-mono'] = plt.subplot(gs[1,i], sharex=ax['color'], sharey=ax['color'])
    for k in ax:
        plt.sca(ax[k])
        plt.axis('off')

    for k in colors:
        ax[k+'-gray'].imshow(locals()[k], cmap=il.one2another('black', 'white'), origin=origin)
        ax[k+'-mono'].imshow(locals()[k], cmap=il.one2another('black', k), origin=origin)
        ax[k+'-gray'].set_title(k)

    ax['color'].imshow(compile_rgb(red,green,blue), origin=origin)

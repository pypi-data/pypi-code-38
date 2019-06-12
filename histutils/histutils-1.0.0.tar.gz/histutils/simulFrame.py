"""
functions for loading HST real camera raw data
 michael hirsch 2014, ported from Matlab code

INPUT FILE FORMAT: intended for use with "DMCdata" raw format, 4-byte
 "footer" containing frame index (must use typecast)
"""
import logging
from datetime import datetime
from time import time
import h5py
from numpy import arange, unique, atleast_1d, around, array, isfinite
from scipy.interpolate import interp1d
# local
from .get1Dcut import get1Dcut


def getSimulData(sim, cam, odir=None, verbose=0):
    # %% synchronize
    cam, sim = HSTsync(sim, cam, verbose)
# %% load 1-D cut slices into keogram array
    cam, rawdata = HSTframeHandler(sim, cam, odir, verbose)
    return cam, rawdata, sim


def HSTsync(sim, cam, verbose):
    """ this function now uses UT1 time -- seconds since 1970 Jan 1
    """
    try:
        if isinstance(sim.startutc, datetime):
            reqStart = sim.startutc.timestamp()
            reqStop = sim.stoputc.timestamp()
        elif isinstance(sim.startutc, (float, int)):  # ut1_unix
            reqStart = sim.startutc
            reqStop = sim.stoputc
        else:
            raise TypeError('unknown time request format')
    except AttributeError:  # no specified start,stop, but is there a specifed time list?
        try:
            treqlist = atleast_1d(sim.treqlist)
            if isinstance(treqlist[0], datetime):
                treqlist = array([t.timestamp() for t in treqlist])
            elif isinstance(treqlist[0], (float, int)):
                pass  # already ut1_unix
            elif isinstance(treqlist[0], str):
                raise TypeError('parse dates before passing them in here')
            else:
                logging.error(
                    'I did not understand your time request, falling back to all times')
                reqStart = 0.  # arbitrary time in the past
                reqStop = 3e9  # arbitrary time in the future
        except AttributeError:
            reqStart = 0.  # arbitrary time in the past
            reqStop = 3e9  # arbitrary time in the future
# %% determine mutual start/stop frame
# FIXME: assumes that all cameras overlap in time at least a little.
# we will play only over UTC times for which both sites have frames available
    # who started last
    mutualStart = max([C.filestartutc for C in cam if C.usecam])
    mutualStop = min([C.filestoputc for C in cam if C.usecam]
                     )  # who ended first
# %% make playback time steps
    """
    based on the "simulated" UTC times that do not necessarily correspond exactly
    with either camera.
    """
    tall = arange(mutualStart, mutualStop, sim.kineticsec)

    logging.info(f'{tall.size} mutual frames available '
                 f'from {datetime.utcfromtimestamp(mutualStart)}'
                 f'to {datetime.utcfromtimestamp(mutualStop)}')
# %% adjust start/stop to user request
    try:
        treq = treqlist
    except NameError:
        # keep greater than start time
        treq = tall[(tall > reqStart) & (tall < reqStop)]

    assert len(treq) > 0, 'did not find any times within your limits'

    logging.info('Per user specification, analyzing {} frames from {} to {}'.format(
        treq.size, treq[0], treq[-1]))
# %% use *nearest neighbor* interpolation to find mutual frames to display.
    """ sometimes one camera will have frames repeated, while the other camera
    might skip some frames altogether
    """
    for C in cam:
        if C.usecam:
            ft = interp1d(C.ut1unix,
                          arange(C.ut1unix.size, dtype=int),
                          kind='nearest',
                          bounds_error=False)

            ind = around(ft(treq))
            ind = ind[isfinite(ind)]  # discard requests outside of file bounds
            # these are the indices for each time (the slower camera will use some frames twice in a row)
            C.pbInd = ind.astype(int)
            print('using frames {} to {} for camera {}'.format(
                C.pbInd[0], C.pbInd[-1], C.name))

    sim.nTimeSlice = treq.size

    return cam, sim


def HSTframeHandler(sim, cam, odir=None, verbose=0):
    # %% load 1D cut coord (only for histfeas)
    try:
        cam = get1Dcut(cam, odir, verbose)
    except (AttributeError, OSError):
        pass
# %% use 1D cut coord
    logging.info('frameHandler: Loading and 1-D cutting data...')
    tic = time()
    rawdata = []  # one list element for each camera, of varying number of frames
    for C in cam:
        if not C.usecam:
            continue
        """
        This two-step indexing if repeated frames is 40 times faster to read at once,
        even with this indexing trick than frame by frame
        """
        ind = unique(C.pbInd)
        if len(ind) < 1:
            continue
        # http://docs.h5py.org/en/latest/high/dataset.html#fancy-indexing
        # IOError: Can't read data (Src and dest data spaces have different sizes)
        # if you have repeated index in fancy indexing
        with h5py.File(str(C.fn), 'r', libver='latest') as f:
            im = f['/rawimg'][ind, ...]
            # in case repeated frames selected, which h5py 2.5 can't handle (fancy indexing, non-increasing)
            if ind.size != C.pbInd.size:
                # FIXME allows repeated indexes which h5py 2.5 does not for mmap
                im = im[C.pbInd - ind[0], ...]
            im = C.doorientimage(im)
            rawdata.append(im)
# %% assign slice & time to class variables
            # NOTE C.ut1unix is timeshift corrected, f['/ut1_unix'] is UNcorrected!
            # need value for non-Boolean indexing (as of h5py 2.5)
            C.tKeo = C.ut1unix[C.pbInd]

            """
            C.cutrow, C.cutcol only exist if running from histfeas program, not used otherwise
            DON'T use try-except AttributeError as that's too broad and causes confusion
            """
            if hasattr(C, 'cutrow'):
                if im.ndim == 3:
                    C.keo = im[:, C.cutrow, C.cutcol].T  # row = pix, col = time
                elif im.ndim == 2:
                    C.keo = im[C.cutrow, C.cutcol].T
                else:
                    raise ValueError('ndim==2 or 3')

    logging.debug(f'Loaded all image frames in {time() - tic:.2f} sec.')

    return cam, rawdata

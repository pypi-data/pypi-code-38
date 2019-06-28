from pathlib import Path
from dateutil.parser import parse
import re
import numpy as np

try:
    import tifffile
except ImportError:
    tifffile = None
try:
    from astropy.io import fits
except ImportError:
    fits = None

from .rawDMCreader import howbig, whichframes
from .timedmc import frame2ut1


def getNeoParam(fn, FrameIndReq=None, ut1req=None, kineticsec=None, startUTC=None, cmosinit={}, verbose=False):
    """
    assumption is that this is a Neo sCMOS FITS / TIFF file, where Solis chooses to break up the recordings
    into smaller files. Verify if this timing estimate makes sense for your application!
    I did not want to do regexp on the filename or USERTXT1 as I felt this too prone to error.

    inputs:
    -------
    cmosinit = {'firstrawind','lastrawind'}
    """
    fn = Path(fn).expanduser()

    nHeadBytes = 0

    if fn.suffix.lower() in '.tiff':
        if tifffile is None:
            raise ImportError('tifffile')
        # FIXME didn't the 2011 TIFFs have headers? maybe not.
        with tifffile.TiffFile(str(fn)) as f:
            Y, X = f[0].shape
            cmosinit = {'firstrawind': 1,
                        'lastrawind': len(f)}
    elif fn.suffix.lower() in '.fits':
        if tifffile is None:
            raise ImportError('astropy')

        with fits.open(fn, mode='readonly', memmap=False) as f:

            kineticsec = f[0].header['KCT']
            # TODO start of night's recording (with some Solis versionss)
            startseries = parse(f[0].header['DATE'] + 'Z')

            # TODO wish there was a better way
            try:
                frametxt = f[0].header['USERTXT1']
                m = re.search(r'(?<=Images\:)\d+-\d+(?=\.)', frametxt)
                inds = m.group(0).split('-')
            except KeyError:  # just a single file?
                # yes start with 1, end without adding 1 for Andor Solis
                inds = [1, f[0].shape[0]]

            cmosinit = {'firstrawind': int(inds[0]),
                        'lastrawind': int(inds[1])}

            # start = parse(f[0].header['FRAME']+'Z') No, incorrect by several hours with some 2015 Solis versions!

            Y, X = f[0].shape[-2:]

        startUTC = startseries.timestamp()

# %% FrameInd relative to this file
    PixelsPerImage, BytesPerImage, BytesPerFrame = howbig(X, Y, nHeadBytes)

    FrameIndRel = whichframes(fn, FrameIndReq, kineticsec, ut1req, startUTC,
                              cmosinit['firstrawind'], cmosinit['lastrawind'],
                              BytesPerImage, BytesPerFrame, verbose)

    assert isinstance(
        FrameIndReq, int) or FrameIndReq is None, 'TODO: add multi-frame request case'
    rawFrameInd = np.arange(cmosinit['firstrawind'],
                            cmosinit['lastrawind'] + 1,
                            FrameIndReq, dtype=np.int64)

    finf = {'superx': X,
            'supery': Y,
            'nframeextract': FrameIndRel.size,
            'nframe': rawFrameInd.size,
            'frameindrel': FrameIndRel,
            'frameind': rawFrameInd,
            'kineticsec': kineticsec}
# %% absolute frame timing (software, yikes)
    finf['ut1'] = frame2ut1(startUTC, kineticsec, rawFrameInd)

    return finf

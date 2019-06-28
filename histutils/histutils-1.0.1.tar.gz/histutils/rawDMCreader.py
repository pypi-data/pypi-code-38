#!/usr/bin/env python
"""
reads .DMCdata files and displays them

NOTE: Observe the dtype=np.int64, this is for Windows Python, that wants to
   default to int32 instead of int64 like everyone else!
"""
from pathlib import Path
import logging
import numpy as np
from typing import Dict, Any, Tuple, Union
from typing.io import BinaryIO
#
from .utils import write_quota
from .io import imgwriteincr, setupimgh5
from .index import getRawInd, meta2rawInd, req2frame
from .timedmc import frame2ut1, ut12frame
#
BPP = 16  # bits per pixel
# NHEADBYTES = 4


def goRead(infn: Path,
           params: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:

    infn = Path(infn).expanduser()
# %% setup data parameters
    # preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
    finf = getDMCparam(infn, params)
    write_quota(finf['bytes_frame'] * finf['nframeextract'], params.get('outfn'))

    rawFrameInd = np.zeros(finf['nframeextract'], dtype=np.int64)
# %% output (variable or file)
    if params.get('outfn'):
        setupimgh5(params['outfn'], finf)
        data = None
    else:
        data = np.zeros((finf['nframeextract'], finf['super_y'], finf['super_x']),
                        dtype=np.uint16, order='C')
# %% read
    with infn.open('rb') as fid:
        # j and i are NOT the same in general when not starting from beginning of file!
        for j, i in enumerate(finf['frameindrel']):
            D, rawFrameInd[j] = getDMCframe(fid, i, finf)
            if params.get('outfn'):
                imgwriteincr(params['outfn'], D, j)
            else:
                data[j, ...] = D
# %% absolute time estimate, software timing (at your peril)
    finf['ut1'] = frame2ut1(params.get('startUTC'), params.get('kineticraw'), rawFrameInd)

    return data, rawFrameInd, finf


def getDMCparam(fn: Path, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    nHeadBytes=4 for 2013-2016 data
    nHeadBytes=0 for 2011 data
    """
    finf = {'nmetadata': params['header_bytes'] // 2,
            'header_bytes': params['header_bytes']}  # FIXME for DMCdata version 1 only

    if not fn.is_file():  # leave this here, getsize() doesn't fail on directory
        raise FileNotFoundError(fn)

    # int() in case we are fed a float or int
    finf['super_x'] = int(params['xy_pixel'][0] // params['xy_bin'][0])
    finf['super_y'] = int(params['xy_pixel'][1] // params['xy_bin'][1])

    finf.update(howbig(params, finf))

    finf['first_frame'], finf['last_frame'] = getRawInd(fn, finf)

    FrameIndRel = whichframes(fn, params, finf)

    finf['nframeextract'] = FrameIndRel.size
    finf['frameindrel'] = FrameIndRel

    return finf


def howbig(params: Dict[str, Any], finf: Dict[str, Any]) -> Dict[str, int]:

    sizes = {'pixels_image': finf['super_x'] * finf['super_y']}
    sizes['bytes_image'] = sizes['pixels_image'] * BPP // 8
    sizes['bytes_frame'] = sizes['bytes_image'] + params['header_bytes']

    return sizes


def whichframes(fn: Path,
                params: Dict[str, Any],
                finf: Dict[str, Any]) -> np.ndarray:

    fileSizeBytes = fn.stat().st_size

    if fileSizeBytes < finf['bytes_image']:
        raise ValueError(f'File size {fileSizeBytes} is smaller than a single image frame!')

    if fileSizeBytes % finf['bytes_frame']:
        logging.error("Either the file is truncated, or I am not reading this file correctly."
                      f"\n bytes per frame: {finf['bytes_frame']:d}")

    first_frame, last_frame = getRawInd(fn, finf)

    if fn.suffix == '.DMCdata':
        nFrame = fileSizeBytes // finf['bytes_frame']
        logging.info(f'{nFrame} frames, Bytes: {fileSizeBytes} in file {fn}')

        nFrameRaw = (last_frame - first_frame + 1)
        if nFrameRaw != nFrame:
            logging.warning(f'there may be missed frames: nFrameRaw {nFrameRaw}   nFrame {nFrame}')
    else:  # CMOS
        nFrame = last_frame - first_frame + 1

    allrawframe = np.arange(first_frame, last_frame + 1, 1, dtype=np.int64)
    logging.info(f"first / last raw frame #'s: {first_frame}  / {last_frame} ")
# %% absolute time estimate
    ut1_unix_all = frame2ut1(params.get('startUTC'), params.get('kineticsec'), allrawframe)
# %% setup frame indices
    """
    if no requested frames were specified, read all frames. Otherwise, just
    return the requested frames
    Assignments have to be "int64", not just python "int".
    Windows python 2.7 64-bit on files >2.1GB, the bytes will wrap
    """
    FrameIndRel = ut12frame(params.get('ut1req'),
                            np.arange(0, nFrame, 1, dtype=np.int64),
                            ut1_unix_all)

    # NOTE: no ut1req or problems with ut1req, canNOT use else, need to test len() in case index is [0] validly
    if FrameIndRel is None or len(FrameIndRel) == 0:
        FrameIndRel = req2frame(params.get('frame_request'), nFrame)

    badReqInd = (FrameIndRel > nFrame) | (FrameIndRel < 0)
# check if we requested frames beyond what the BigFN contains
    if badReqInd.any():
        # don't include frames in case of None
        raise ValueError(f'frames requested outside the times covered in {fn}')

    nFrameExtract = FrameIndRel.size  # to preallocate properly
    bytes_extract = nFrameExtract * finf['bytes_frame']
    logging.info(f'Extracted {nFrameExtract} frames from {fn} totaling {bytes_extract / 1e9:.2f} GB.')

    if bytes_extract > 4e9 and 'outfn' not in params:
        logging.info(f'This will require {bytes_extract / 1e9:.2f} GB of RAM.')

    return FrameIndRel


def getDMCframe(f: Union[BinaryIO, Path], iFrm: int, finf: Dict[str, int]) -> Tuple[np.ndarray, int]:
    """
    read a single image frame

    Parameters
    ----------
    f: pathlib.Path or BinaryIO
        open file handle or file path
    """
    if isinstance(f, Path):
        if not f.is_file():  # need for Windows PermissionError
            raise FileNotFoundError(f)
        with f.open('rb') as g:
            return getDMCframe(g, iFrm, finf)
    # on windows, "int" is int32 and overflows at 2.1GB!  We need np.int64
    currByte = iFrm * finf['bytes_frame']
# %% advance to start of frame in bytes
    logging.debug(f'seeking to byte {currByte}')

    if not isinstance(iFrm, (int, np.int64)):
        raise TypeError('int32 will fail on files > 2GB')

    try:
        f.seek(currByte, 0)
    except OSError as e:
        raise OSError(f'could not seek to byte {currByte:d}. try using a 64-bit integer for iFrm \n'
                      f'is {f.name} a DMCdata file?  {e}')
# %% read data ***LABVIEW USES ROW-MAJOR C ORDERING!!
    try:
        currFrame = np.fromfile(f, np.uint16,
                                finf['pixels_image']).reshape((finf['super_y'], finf['super_x']), order='C')
    except ValueError as e:
        raise ValueError(f'read past end of file? \n {f.name} \n {e}')

    rawFrameInd = meta2rawInd(f, finf['nmetadata'])

    if rawFrameInd is None:  # 2011 no metadata file
        rawFrameInd = iFrm + 1  # fallback

    return currFrame, rawFrameInd

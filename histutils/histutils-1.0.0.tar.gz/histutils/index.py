from pathlib import Path
import numpy as np
from typing import Tuple, Dict, Sequence
from typing.io import BinaryIO
import logging
from struct import pack, unpack


def getRawInd(fn: Path, params: Dict[str, int]) -> Tuple[int, int]:
    if not isinstance(params['nmetadata'], int):
        raise TypeError(params['nmetadata'])

    if params['nmetadata'] < 1:  # no header, only raw images
        fileSizeBytes = fn.stat().st_size
        if fileSizeBytes % params['bytes_image']:
            logging.error(f'{fn} may not be read correctly, mismatch frame->file size')

        firstRawIndex = 1  # definition, one-based indexing
        lastRawIndex = fileSizeBytes // params['bytes_image']
    else:  # normal case 2013-2016
        # gets first and last raw indices from a big .DMCdata file
        with fn.open('rb') as f:
            f.seek(params['bytes_image'], 0)  # get first raw frame index
            firstRawIndex = meta2rawInd(f, params['nmetadata'])

            if firstRawIndex < 1:
                raise ValueError(firstRawIndex)
            if firstRawIndex > 100_000_000:
                logging.error(f'first index seems impossibly large {firstRawIndex}')
# %%
            f.seek(-params['header_bytes'], 2)  # get last raw frame index
            lastRawIndex = meta2rawInd(f, params['nmetadata'])

            if lastRawIndex < 1:
                raise ValueError(lastRawIndex)
            if lastRawIndex > 100_000_000:
                logging.error(f'last index seems impossibly large {lastRawIndex}')

    return firstRawIndex, lastRawIndex


def meta2rawInd(f: BinaryIO, Nmetadata: int) -> int:

    if Nmetadata < 1:
        rawind = None  # undefined
    else:
        # FIXME works for .DMCdata version 1 only
        metad = np.fromfile(f, dtype=np.uint16, count=Nmetadata)
        metad = pack('<2H', metad[1], metad[0])  # reorder 2 uint16
        rawind = unpack('<I', metad)[0]  # always a tuple

    return rawind


def req2frame(req: Sequence[int], N: int = 0) -> np.ndarray:
    """
    output has to be numpy.arange for > comparison
    """
    if req is None:
        frame = np.arange(N, dtype=np.int64)
    elif isinstance(req, int):  # the user is specifying a step size
        frame = np.arange(0, N, req, dtype=np.int64)
    elif isinstance(req, slice):
        raise TypeError('slice type not allowed, pass in list or tuple with slice ordering (start, stop, step)')
    elif len(req) == 1:
        frame = np.arange(0, N, req[0], dtype=np.int64)
    elif len(req) == 2:
        frame = np.arange(req[0], req[1], dtype=np.int64)
    elif len(req) == 3:
        # this is -1 because user is specifying one-based index
        frame = np.arange(req[0], req[1], req[2],
                          dtype=np.int64) - 1  # keep -1 !
    else:  # just return all frames
        frame = np.arange(N, dtype=np.int64)

    return frame

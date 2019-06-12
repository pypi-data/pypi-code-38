from pathlib import Path
import numpy as np
import h5py
from typing import Union, Dict, Any
from datetime import datetime
import logging


def dir2fn(ofn: Path, ifn: Path, suffix: str = '.h5') -> Path:
    """

    Parameters
    ----------

    ofn: pathlib.Path
        filename or output directory, to create filename based on ifn
    ifn: pathlib.Path
        input filename (don't overwrite!)
    suffix: str, optional
        desired file extension e.g. .h5

    Returns
    -------

    ofn: pathlib.Path
        filename to write
    """
    if not ofn:  # no output file desired
        return None

    ofn = Path(ofn).expanduser()
    ifn = Path(ifn).expanduser()
    if not ifn.is_file():
        raise FileNotFoundError(ifn)

    if ofn.suffix == suffix:  # must already be a filename
        pass
    else:  # must be a directory
        ofn.mkdir(parents=True, exist_ok=True)
        ofn = ofn / ifn.with_suffix(suffix).name

    try:
        if ofn.samefile(ifn):
            raise FileExistsError(f'do not overwrite input file! {ifn}')
    except FileNotFoundError:  # a good thing, the output file doesn't exist and hence it's not the input file
        pass

    return ofn


def imgwriteincr(fn: Path, imgs: np.ndarray,
                 imgslice: Union[int, slice]):
    """
    writes HDF5 huge image files in increments

    Parameters
    ----------

    fn: pathlib.Path
        HDF5 filename to write / append to
    imgs: numpy.ndarray
        image(s) N x X x Y to write
    imgslice: int or slice
        where to write the image(s) in the HDF5 file
    """
    if isinstance(imgslice, int):
        if imgslice and not (imgslice % 2000):
            print(f'appending images {imgslice} to {fn}')

    if isinstance(fn, Path):
        # avoid accidental overwriting of source file due to misspecified command line
        with h5py.File(fn, 'r+') as f:
            f['/rawimg'][imgslice, :, :] = imgs
    elif isinstance(fn, h5py.File):
        f['/rawimg'][imgslice, :, :] = imgs
    else:
        raise TypeError(f'{fn} must be Path or h5py.File instead of {type(fn)}')


def vid2h5(data: np.ndarray, *, ut1, rawind, ticks,
           outfn: Path,
           params: Dict[str, Any],
           i: int = 0,
           Nfile: int = 1, det=None, tstart=None, cmdlog: str = None):

    outfn = Path(outfn).expanduser()
    if outfn.is_dir():
        raise IsADirectoryError(outfn)
    outfn.parent.mkdir(exist_ok=True)

    txtupd = f'convert file {i+1} / {Nfile}'
    if params.get('spoolfn'):
        txtupd += f' {params["spoolfn"].name}'
    txtupd += f' => {outfn}'
    """
    note if line wraps (>80 characters), this in-place update breaks.
    """
    print(txtupd + '\r', end="")
    # %% saving
    """
    Reference: https://www.hdfgroup.org/HDF5/doc/ADGuide/ImageSpec.html
    Thanks to Eric Piel of Delmic for pointing out this spec
    * the HDF5 attributess set are necessary to put HDFView into image mode and enables
    other conforming readers to easily play images stacks as video.
    * the string_() calls are necessary to make fixed length strings per HDF5 spec
    """
    # NOTE write mode r+ to not overwrite incremental images
    if outfn.is_file():
        writemode = 'r+'  # append
    else:
        writemode = 'w'

    if data is not None:
        params['nframeextract'] = data.shape[0] * Nfile
        params['super_y'] = data.shape[1]
        params['super_x'] = data.shape[2]
        ind = slice(i * data.shape[0], (i + 1) * data.shape[0])
    else:  # FIXME haven't reevaluated for update only case
        for q in (ut1, rawind, ticks):
            if q is not None:
                N = len(q)
                break
        ind = slice(None)

    with h5py.File(outfn, writemode) as f:
        if data is not None:
            if 'rawimg' not in f:  # first run
                setupimgh5(f, params)

            f['/rawimg'][ind, ...] = data

        if ut1 is not None:
            print(f'writing from {datetime.utcfromtimestamp(ut1[0])}'
                  f'to {datetime.utcfromtimestamp(ut1[-1])}')
            if 'ut1_unix' not in f:
                fut1 = f.create_dataset(
                    '/ut1_unix', shape=(N,), dtype=float, fletcher32=True)
                fut1.attrs['units'] = 'seconds since Unix epoch Jan 1 1970 midnight'

            f['/ut1_unix'][ind] = ut1

        if tstart is not None and 'tstart' not in f:
            f['/tstart'] = tstart

        if rawind is not None:
            if 'rawind' not in f:
                fri = f.create_dataset('/rawind', shape=(N,), dtype=np.int64, fletcher32=True)
                fri.attrs['units'] = 'one-based index since camera program started this session'

            f['/rawind'][ind] = rawind

        if ticks is not None:
            if 'ticks' not in f:
                ftk = f.create_dataset('/ticks', shape=(N,), dtype=np.uint64, fletcher32=True)  # Uint64
                ftk.attrs['units'] = 'FPGA tick counter for each image frame'

            f['/ticks'][ind] = ticks

        if params.get('spoolfn'):
            # http://docs.h5py.org/en/latest/strings.html
            if 'spoolfn' not in f:
                fsp = f.create_dataset('/spoolfn', shape=(N,), dtype=h5py.special_dtype(vlen=bytes))
                fsp.attrs['description'] = 'input filename data was extracted from'

            f['/spoolfn'][ind] = params['spoolfn'].name

        if det is not None:
            if 'detect' not in f:
                fdt = f.create_dataset('/detect', shape=(N,), dtype=int)
                fdt.attrs['description'] = '# of auroral detections this frame'

            f['/detect'][i] = det[i]

        if 'params' not in f:
            cparam = np.array((
                params['kineticsec'],
                params['rotccw'],
                params['transpose'],
                params['flipud'],
                params['fliplr'],
                1),
                dtype=[('kineticsec', 'f8'),
                       ('rotccw', 'i1'),
                       ('transpose', 'i1'),
                       ('flipud', 'i1'),
                       ('fliplr', 'i1'),
                       ('questionable_ut1', 'i1')]
            )

            # cannot use fletcher32 here, typeerror
            f.create_dataset('/params', data=cparam)

        if 'sensorloc' not in f and params.get('sensorloc'):
            loc = params['sensorloc']
            try:
                lparam = np.array((loc[0], loc[1], loc[2]),
                                  dtype=[('lat', 'f8'), ('lon', 'f8'), ('alt_m', 'f8')])

                # cannot use fletcher32 here, typeerror
                Ld = f.create_dataset('/sensorloc', data=lparam)
                Ld.attrs['units'] = 'WGS-84 lat (deg),lon (deg), altitude (meters)'
            except (IndexError, TypeError) as e:
                logging.error(f'could not write sensor position {e}')

        if 'cmdlog' not in f:
            if isinstance(cmdlog, (tuple, list)):
                cmdlog = ' '.join(cmdlog)
            # cannot use fletcher32 here, typeerror
            f['/cmdlog'] = str(cmdlog)

        if 'header' not in f and params.get('header'):
            f['/header'] = str(params['header'])

        if 'hdf5version' not in f:
            f['/hdf5version'] = h5py.version.hdf5_version_tuple


def setupimgh5(f: Union[Path, h5py.File], params: Dict[str, int], *,
               dtype=np.uint16,
               writemode: str = 'r+',
               key: str = '/rawimg',
               cmdlog: str = None):
    """
    Configures an HDF5 file for storing image stacks, enabling video player in
    HDF5 readers so equipped

    Parameters
    ----------
    f: HDF5 handle (or filename)

    h: HDF5 dataset handle
    """
    if isinstance(f, (str, Path)):  # assume new HDF5 file wanted
        f = Path(f).expanduser()
        if f.is_dir():
            raise IsADirectoryError(f)
        if not f.is_file():
            writemode = 'w'

        with h5py.File(f, writemode) as F:
            setupimgh5(F, params, dtype=dtype, writemode=writemode, key=key)

    elif isinstance(f, h5py.File):
        Nrow, Ncol = params['super_y'], params['super_x']

        h = f.create_dataset(key,
                             shape=(params['nframeextract'], Nrow, Ncol),
                             dtype=dtype,
                             chunks=(1, Nrow, Ncol),  # each image is a chunk
                             compression='gzip',
                             # no difference in filesize from 1 to 5, except much faster to use lower numbers!
                             compression_opts=1,
                             shuffle=True,
                             fletcher32=True,
                             track_times=True)
        h.attrs["CLASS"] = np.string_("IMAGE")
        h.attrs["IMAGE_VERSION"] = np.string_("1.2")
        h.attrs["IMAGE_SUBCLASS"] = np.string_("IMAGE_GRAYSCALE")
        h.attrs["DISPLAY_ORIGIN"] = np.string_("LL")
        h.attrs['IMAGE_WHITE_IS_ZERO'] = np.uint8(0)

        if cmdlog and isinstance(cmdlog, str):
            f['/cmdlog'] = cmdlog
    else:
        raise TypeError(f'{type(f)} is not correct, must be filename or h5py.File HDF5 file handle')

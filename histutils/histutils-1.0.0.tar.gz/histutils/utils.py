from pathlib import Path
import numpy as np
import shutil


def write_quota(outbytes: int, outfn: Path) -> int:
    """
    aborts writing if not enough space on drive to write
    """
    if not outfn:
        return None

    anch = Path(outfn).resolve().anchor
    freeout = shutil.disk_usage(anch).free

    if freeout < 4 * outbytes or freeout < 10e9:
        raise OSError(f'low disk space on {anch}\n'
                      f'{freeout/1e9:.1f} GByte free, wanting to write {outbytes/1e9:.2f} GByte to {outfn}.')

    return freeout


def sixteen2eight(I: np.ndarray, Clim: tuple) -> np.ndarray:
    """
    scipy.misc.bytescale had bugs

    inputs:
    ------
    I: 2-D Numpy array of grayscale image data
    Clim: length 2 of tuple or numpy 1-D array specifying lowest and highest expected values in grayscale image
    Michael Hirsch, Ph.D.
    """
    Q = normframe(I, Clim)
    Q *= 255  # stretch to [0,255] as a float
    return Q.round().astype(np.uint8)  # convert to uint8


def normframe(I: np.ndarray, Clim: tuple) -> np.ndarray:
    """
    inputs:
    -------
    I: 2-D Numpy array of grayscale image data
    Clim: length 2 of tuple or numpy 1-D array specifying lowest and highest expected values in grayscale image
    """
    Vmin = Clim[0]
    Vmax = Clim[1]

    # stretch to [0,1]
    return (I.astype(np.float32).clip(Vmin, Vmax) - Vmin) / (Vmax - Vmin)


def splitconf(conf, key, i=None, dtype=float, fallback=None, sep=','):
    if conf is None:
        return fallback

    if isinstance(conf, dict):
        try:
            return conf[key][i]
        except TypeError:
            return conf[key]
        except KeyError:
            return fallback

    if i is not None:
        assert isinstance(i, (int, slice)), 'single integer index only'

    if isinstance(key, (tuple, list)):
        if len(key) > 1:  # drilldown
            return splitconf(conf[key[0]], key[1:], i, dtype, fallback, sep)
        else:
            return splitconf(conf, key[0], i, dtype, fallback, sep)
    elif isinstance(key, str):
        val = conf.get(key, fallback=fallback)
    else:
        raise TypeError(f'invalid key type {type(key)}')

    try:
        return dtype(val.split(sep)[i])
    except (ValueError, AttributeError, IndexError):
        return fallback
    except TypeError:
        if i is None:
            try:
                # return list of all values instead of just one
                return [dtype(v) for v in val.split(sep)]
            except ValueError:
                return fallback
        else:
            return fallback

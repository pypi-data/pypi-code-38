"""Predictors for reverse correlation"""
# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import numpy as np

from .._data_obj import NDVar, Case, UTS, asndvar, asarray


def epoch_impulse_predictor(shape, value=1, latency=0, name=None, ds=None):
    """Generate impulse predictor with one impulse for each of ``n`` epochs

    Parameters
    ----------
    shape : NDVar | (int, UTS) | str
        Shape of the output. Can be specified as the :class:`NDVar` with the
        data to predict, or an ``(n_cases, time_dimension)`` tuple.
    value : scalar | sequence | str
        Scalar or length ``n`` sequence of scalars specifying the value of each
        impulse (default 1).
    latency : scalar | sequence | str
        Scalar or length ``n`` sequence of scalars specifying the latency of
        each impulse (default 0).
    name : str
        Name for the output :class:`NDVar`.
    ds : Dataset
        If specified, input items (``shape``, ``value`` and ``latency``) can be
        strings to be evaluated in ``ds``.

    Examples
    --------
    Generate impulse predictors for categorial data::

    >>> ds = datasets.get_uts()
    >>> p1 = epoch_impulse_predictor('uts', 'A=="a1"', name='a1', ds=ds)
    >>> p0 = epoch_impulse_predictor('uts', 'A=="a0"', name='a0', ds=ds)
    >>> p1 = p1.smooth('time', .05, 'hamming')
    >>> p0 = p0.smooth('time', .05, 'hamming')
    >>> res = boosting('uts', [p1, p0], 0, 0.5, model='A', ds=ds)
    >>> plot.UTS([[h.smooth('time', 0.05) for h in res.h]])

    """
    if isinstance(shape, str):
        shape = asndvar(shape, ds=ds)
    if isinstance(value, str):
        value = asarray(value, ds=ds)
    if isinstance(latency, str):
        latency = asarray(latency, ds=ds)

    if isinstance(shape, NDVar):
        if not shape.has_case:
            raise ValueError(f'shape={shape!r}: has no case dimension')
        n = len(shape)
        time = shape.get_dim('time')
    else:
        n, time = shape
        if not isinstance(time, UTS):
            raise TypeError(f'shape={shape!r}: second item needs to be UTS instance')

    x = np.zeros((n, len(time)))
    t_index = time._array_index(latency)
    if np.isscalar(latency):
        x[:, t_index] = value
    else:
        x[np.arange(n), t_index] = value
    return NDVar(x, (Case, time), {}, name)

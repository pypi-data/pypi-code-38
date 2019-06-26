"""
Boosting as described by David et al. (2007).

Versions
--------
7: Accept segmented data, respect segmentation (don't concatenate data)


Profiling
---------
ds = datasets._get_continuous()
y = ds['y']
x1 = ds['x1']
x2 = ds['x2']

%prun -s cumulative res = boosting(y, x1, 0, 1)

"""
import inspect
from itertools import product
from multiprocessing import Process, Queue
from multiprocessing.sharedctypes import RawArray
import os
import time
from threading import Event, Thread

import numpy as np
from numpy import newaxis
from scipy.linalg import norm
import scipy.signal
from scipy.stats import spearmanr
from tqdm import tqdm

from .._config import CONFIG
from .._data_obj import NDVar
from .._utils import LazyProperty, user_activity
from ._boosting_opt import l1, l2, generate_options, update_error
from .shared import RevCorrData


# BoostingResult version
VERSION = 9

# process messages
JOB_TERMINATE = -1

# error functions
ERROR_FUNC = {'l2': l2, 'l1': l1}
DELTA_ERROR_FUNC = {'l2': 2, 'l1': 1}


class BoostingResult:
    """Result from boosting a temporal response function

    Attributes
    ----------
    h : NDVar | tuple of NDVar
        The temporal response function. Whether ``h`` is an NDVar or a tuple of
        NDVars depends on whether the ``x`` parameter to :func:`boosting` was
        an NDVar or a sequence of NDVars.
    h_scaled : NDVar | tuple of NDVar
        ``h`` scaled such that it applies to the original input ``y`` and ``x``.
        If boosting was done with ``scale_data=False``, ``h_scaled`` is the same
        as ``h``.
    h_source : NDVar | tuple of NDVar
        If ``h`` was constructed using a basis, ``h_source`` represents the
        source of ``h`` before being convolved with the basis.
    h_time : UTS
        Time dimension of the kernel.
    r : float | NDVar
        Correlation between the measured response and the response predicted
        with ``h``. Type depends on the ``y`` parameter to :func:`boosting`.
    spearmanr : float | NDVar
        As ``r``, the Spearman rank correlation.
    t_run : float
        Time it took to run the boosting algorithm (in seconds).
    error : str
        The error evaluation method used.
    residual : float | NDVar
        The fit error, i.e. the result of the ``error`` error function on the
        final fit.
    delta : scalar
        Kernel modification step used.
    mindelta : None | scalar
        Mindelta parameter used.
    scale_data : bool
        Scale_data parameter used.
    y_mean : NDVar | scalar
        Mean that was subtracted from ``y``.
    y_scale : NDVar | scalar
        Scale by which ``y`` was divided.
    x_mean : NDVar | scalar | tuple
        Mean that was subtracted from ``x``.
    x_scale : NDVar | scalar | tuple
        Scale by which ``x`` was divided.
    partitions : int
        Numbers of partitions of the data used for cross validation.
    """
    def __init__(
            self,
            # input parameters
            y, x, tstart, tstop, scale_data, delta, mindelta, error,
            basis, basis_window, partitions_arg, partitions, model,
            # result parameters
            h, r, isnan, spearmanr, residual, t_run,
            y_mean, y_scale, x_mean, x_scale, y_info={}, r_l1=None,
            # new parameters
            selective_stopping=0,
            **debug_attrs,
    ):
        # input parameters
        self.y = y
        self.x = x
        self.tstart = tstart
        self.tstop = tstop
        self.scale_data = scale_data
        self.delta = delta
        self.mindelta = mindelta
        self.error = error
        self._partitions_arg = partitions_arg
        self.partitions = partitions
        self.model = model
        self.basis = basis
        self.basis_window = basis_window
        self.selective_stopping = selective_stopping
        # results
        self._h = h
        self._y_info = y_info
        self.r = r
        self.r_l1 = r_l1
        self._isnan = isnan
        self.spearmanr = spearmanr
        self.residual = residual
        self.t_run = t_run
        self.y_mean = y_mean
        self.y_scale = y_scale
        self.x_mean = x_mean
        self.x_scale = x_scale
        self._debug_attrs = debug_attrs
        for k, v in debug_attrs.items():
            setattr(self, k, v)

    def __getstate__(self):
        return {
            # input parameters
            'y': self.y, 'x': self.x, 'tstart': self.tstart, 'tstop': self.tstop,
            'scale_data': self.scale_data, 'delta': self.delta,
            'mindelta': self.mindelta, 'error': self.error,
            'partitions_arg': self._partitions_arg, 'partitions': self.partitions,
            'model': self.model, 'basis': self.basis,
            'basis_window': self.basis_window,
            'selective_stopping': self.selective_stopping,
            # results
            'h': self._h, 'r': self.r, 'r_l1': self.r_l1, 'isnan': self._isnan,
            'spearmanr': self.spearmanr, 'residual': self.residual,
            't_run': self.t_run, 'version': VERSION,
            'y_mean': self.y_mean, 'y_scale': self.y_scale,
            'x_mean': self.x_mean, 'x_scale': self.x_scale,
            'y_info': self._y_info,
            **self._debug_attrs,
        }

    def __setstate__(self, state):
        if state['version'] < 7:
            state.update(partitions=None, partitions_arg=None, model=None, basis=0, basis_window='hamming')
        elif state['version'] < 8:
            state['partitions'] = state.pop('n_partitions')
            state['partitions_arg'] = state.pop('n_partitions_arg')
        if state['version'] < 9:
            state['residual'] = state.pop('fit_error')
        self.__init__(**state)

    def __repr__(self):
        if self.x is None or isinstance(self.x, str):
            x = self.x
        else:
            x = ' + '.join(map(str, self.x))
        items = [
            'boosting %s ~ %s' % (self.y, x),
            '%g - %g' % (self.tstart, self.tstop),
        ]
        for name, param in inspect.signature(boosting).parameters.items():
            if param.default is inspect.Signature.empty or name == 'ds':
                continue
            elif name == 'debug':
                continue
            elif name == 'partitions':
                value = self._partitions_arg
            else:
                value = getattr(self, name)
            if value != param.default:
                items.append(f'{name}={value}')
        return f"<{', '.join(items)}>"

    @LazyProperty
    def h(self):
        if not self.basis:
            return self._h
        elif isinstance(self._h, tuple):
            return tuple(h.smooth('time', self.basis, self.basis_window, 'full') for h in self._h)
        else:
            return self._h.smooth('time', self.basis, self.basis_window, 'full')

    @LazyProperty
    def h_scaled(self):
        if self.y_scale is None:
            return self.h
        elif isinstance(self.h, NDVar):
            out = self.h * (self.y_scale / self.x_scale)
            out.info = self._y_info.copy()
            return out
        else:
            out = []
            for h, sx in zip(self.h, self.x_scale):
                h = h * (self.y_scale / sx)
                h.info = self._y_info.copy()
                out.append(h)
            return tuple(out)

    @LazyProperty
    def h_source(self):
        if self.basis:
            return self._h
        else:
            return None

    @LazyProperty
    def h_time(self):
        if isinstance(self.h, NDVar):
            return self.h.time
        else:
            return self.h[0].time

    def _set_parc(self, parc):
        """Change the parcellation of source-space result
         
        Notes
        -----
        No warning for missing sources!
        """
        from .._ndvar import set_parc

        if not self.r.has_dim('source'):
            raise RuntimeError('BoostingResult does not have source-space data')

        def sub_func(obj):
            if obj is None:
                return None
            elif isinstance(obj, tuple):
                return tuple(sub_func(obj_) for obj_ in obj)
            obj_new = set_parc(obj, parc)
            index = np.invert(obj_new.source.parc.startswith('unknown-'))
            return obj_new.sub(source=index)

        for attr in ('h', 'r', 'spearmanr', 'residual', 'y_mean', 'y_scale'):
            setattr(self, attr, sub_func(getattr(self, attr)))


@user_activity
def boosting(y, x, tstart, tstop, scale_data=True, delta=0.005, mindelta=None,
             error='l2', basis=0, basis_window='hamming',
             partitions=None, model=None, ds=None, selective_stopping=0,
             debug=False):
    """Estimate a filter with boosting

    Parameters
    ----------
    y : NDVar
        Signal to predict.
    x : NDVar | sequence of NDVar
        Signal to use to predict ``y``. Can be sequence of NDVars to include
        multiple predictors. Time dimension must correspond to ``y``.
    tstart : float
        Start of the TRF in seconds.
    tstop : float
        Stop of the TRF in seconds.
    scale_data : bool | 'inplace'
        Scale ``y`` and ``x`` before boosting: subtract the mean and divide by
        the standard deviation (when ``error='l2'``) or the mean absolute
        value (when ``error='l1'``). With ``scale_data=True`` (default) the
        original ``y`` and ``x`` are left untouched; use ``'inplace'`` to save
        memory by scaling the original ``y`` and ``x``.
    delta : scalar
        Step for changes in the kernel.
    mindelta : scalar
        If the error for the training data can't be reduced, divide ``delta``
        in half until ``delta < mindelta``. The default is ``mindelta = delta``,
        i.e. ``delta`` is constant.
    error : 'l2' | 'l1'
        Error function to use (default is ``l2``).
    basis : float
        Use a basis of windows with this length for the kernel (by default,
        impulses are used).
    basis_window : str | float | tuple
        Basis window (see :func:`scipy.signal.get_window` for options; default
        is ``'hamming'``).
    partitions : int
        Divide the data into this many ``partitions`` for cross-validation-based
        early stopping. In each partition, ``n - 1`` segments are used for
        training, and the remaining segment is used for validation.
        If data is continuous, data are divided into contiguous segments of
        equal length (default 10).
        If data has cases, cases are divided with ``[::partitions]`` slices
        (default ``min(n_cases, 10)``; if ``model`` is specified, ``n_cases``
        is the lowest number of cases in any cell of the model).
    model : Categorial
        If data has cases, divide cases into different categories (division
        for crossvalidation is done separately for each cell).
    ds : Dataset
        If provided, other parameters can be specified as string for items in
        ``ds``.
    selective_stopping : int
        By default, the boosting algorithm stops when the testing error stops
        decreasing. With ``selective_stopping=True``, boosting continues but
        excludes the predictor (one time-series in ``x``) that caused the
        increase in testing error, and continues until all predictors are
        stopped. The integer value of ``selective_stopping`` determines after
        how many steps with error increases each predictor is excluded.
    debug : bool
        Store additional properties in the result object (increases memory
        consumption).

    Returns
    -------
    result : BoostingResult
        Object containing results from the boosting estimation (see
        :class:`BoostingResult`).

    Notes
    -----
    In order to predict data, use the :func:`convolve` function::

    >>> ds = datasets.get_uts()
    >>> ds['a1'] = epoch_impulse_predictor('uts', 'A=="a1"', ds=ds)
    >>> ds['a0'] = epoch_impulse_predictor('uts', 'A=="a0"', ds=ds)
    >>> res = boosting('uts', ['a0', 'a1'], 0, 0.5, partitions=10, model='A', ds=ds)
    >>> y_pred = convolve(res.h_scaled, ['a0', 'a1'], ds=ds)

    The boosting algorithm is described in [1]_.

    References
    ----------
    .. [1] David, S. V., Mesgarani, N., & Shamma, S. A. (2007). Estimating
        sparse spectro-temporal receptive fields with natural stimuli. Network:
        Computation in Neural Systems, 18(3), 191-212.
        `10.1080/09548980701609235 <https://doi.org/10.1080/09548980701609235>`_.
    """
    # check arguments
    mindelta_ = delta if mindelta is None else mindelta
    selective_stopping = int(selective_stopping)
    if selective_stopping < 0:
        raise ValueError(f"selective_stopping={selective_stopping}")

    data = RevCorrData(y, x, error, scale_data, ds)
    data.initialize_cross_validation(partitions, model, ds)
    n_y = len(data.y)
    n_x = len(data.x)

    # TRF extent in indices
    tstep = data.time.tstep
    i_start = int(round(tstart / tstep))
    i_stop = int(round(tstop / tstep))
    trf_length = i_stop - i_start

    if data.segments is None:
        i_skip = trf_length - 1
    else:
        i_skip = 0

    if basis:
        n = int(round(basis / data.time.tstep))
        w = scipy.signal.get_window(basis_window, n, False)
        w /= w.sum()
        for xi in data.x:
            xi[:] = scipy.signal.convolve(xi, w, 'same')

    # progress bar
    n_cv = len(data.cv_segments)
    pbar = tqdm(desc=f"Boosting{f' {n_y} signals' if n_y > 1 else ''}", total=n_y * n_cv, disable=CONFIG['tqdm'])
    t_start = time.time()
    # result containers
    res = np.empty((3, n_y))  # r, rank-r, error
    h_x = np.empty((n_y, n_x, trf_length))
    store_y_pred = bool(data.vector_dim) or debug
    y_pred = np.empty_like(data.y) if store_y_pred else np.empty(data.y.shape[1:])
    # boosting
    if CONFIG['n_workers']:
        # Make sure cross-validations are added in the same order, otherwise
        # slight numerical differences can occur
        job_queue, result_queue = setup_workers(data, i_start, trf_length, delta, mindelta_, error, selective_stopping)
        stop_jobs = Event()
        thread = Thread(target=put_jobs, args=(job_queue, n_y, n_cv, stop_jobs))
        thread.start()

        # collect results
        try:
            h_segs = {}
            for _ in range(n_y * n_cv):
                y_i, seg_i, h = result_queue.get()
                pbar.update()
                if y_i in h_segs:
                    h_seg = h_segs[y_i]
                    h_seg[seg_i] = h
                    if len(h_seg) == n_cv:
                        del h_segs[y_i]
                        hs = [h for h in (h_seg[i] for i in range(n_cv)) if h is not None]
                        if hs:
                            h = np.mean(hs, 0, out=h_x[y_i])
                            y_i_pred = y_pred[y_i] if store_y_pred else y_pred
                            convolve(h, data.x, data.x_pads, i_start, data.segments, y_i_pred)
                            if not data.vector_dim:
                                res[:, y_i] = evaluate_kernel(data.y[y_i], y_i_pred, error, i_skip, data.segments)
                        else:
                            h_x[y_i] = 0
                            if not data.vector_dim:
                                res[:, y_i] = 0
                            if store_y_pred:
                                y_pred[y_i] = 0
                else:
                    h_segs[y_i] = {seg_i: h}
        except KeyboardInterrupt:
            stop_jobs.set()
            raise
    else:
        for y_i, y_ in enumerate(data.y):
            hs = []
            for segments, train, test in data.cv_segments:
                h = boost(y_, data.x, data.x_pads, segments, train, test, i_start, trf_length, delta, mindelta_, error, selective_stopping)
                if h is not None:
                    hs.append(h)
                pbar.update()

            if hs:
                h = np.mean(hs, 0, out=h_x[y_i])
                y_i_pred = y_pred[y_i] if store_y_pred else y_pred
                convolve(h, data.x, data.x_pads, i_start, data.segments, y_i_pred)
                if not data.vector_dim:
                    res[:, y_i] = evaluate_kernel(data.y[y_i], y_i_pred, error, i_skip, data.segments)
            else:
                h_x[y_i] = 0
                if not data.vector_dim:
                    res[:, y_i] = 0
                if store_y_pred:
                    y_pred[y_i] = 0

    pbar.close()
    t_run = time.time() - t_start

    # fit-evaluation statistics
    if data.vector_dim:
        y_vector = data.y.reshape(data.vector_shape)
        y_pred_vector = y_pred.reshape(data.vector_shape)
        # error: distance between actual and modeled
        y_pred_error = norm(y_vector - y_pred_vector, axis=1)
        if error == 'l1':
            errs = y_pred_error.mean(-1)
        elif error == 'l2':
            errs = y_pred_error.std(-1)
        else:
            raise RuntimeError(f"error={error!r}")
        rs, rs_l1 = data.vector_correlation(y_vector, y_pred_vector)
        if rs_l1 is None:
            r_l1 = None
        else:
            r_l1 = data.package_value(rs_l1, 'l1 correlation', meas='r')
        spearmanr = None
    else:
        rs, rrs, errs = res
        r_l1 = None
        spearmanr = data.package_value(rrs, 'rank correlation', meas='r')
    isnan = np.isnan(rs)
    rs[isnan] = 0
    r = data.package_value(rs, 'correlation', meas='r')
    residual = data.package_value(errs, 'fit error')

    y_mean, y_scale, x_mean, x_scale = data.data_scale_ndvars()

    if debug:
        debug_attrs = {
            'y_pred': data.package_y_like(y_pred, 'y-pred'),
        }
    else:
        debug_attrs = {}

    h = data.package_kernel(h_x, tstart)
    model_repr = None if model is None else data.model
    return BoostingResult(
        # input parameters
        data.y_name, data.x_name, tstart, tstop, scale_data, delta, mindelta, error,
        basis, basis_window, partitions, data.partitions, model_repr,
        # result parameters
        h, r, isnan, spearmanr, residual, t_run,
        y_mean, y_scale, x_mean, x_scale, data.y_info,
        # vector results
        r_l1, selective_stopping,
        **debug_attrs)


class BoostingStep:
    __slots__ = ('i_stim', 'i_time', 'delta', 'e_train', 'e_test')

    def __init__(self, i_stim, i_time, delta_signed, e_test, e_train):
        self.i_stim = i_stim
        self.i_time = i_time
        self.delta = delta_signed
        self.e_train = e_train
        self.e_test = e_test


def boost(y, x, x_pads, all_index, train_index, test_index, i_start, trf_length,
          delta, mindelta, error, selective_stopping=0, return_history=False):
    """Estimate one filter with boosting

    Parameters
    ----------
    y : array (n_times,)
        Dependent signal, time series to predict.
    x : array (n_stims, n_times)
        Stimulus.
    x_pads : array (n_stims,)
        Padding for x.
    train_index : array of (start, stop)
        Time sample index of training segments.
    test_index : array of (start, stop)
        Time sample index of test segments.
    trf_length : int
        Length of the TRF (in time samples).
    delta : scalar
        Step of the adjustment.
    mindelta : scalar
        Smallest delta to use. If no improvement can be found in an iteration,
        the first step is to divide delta in half, but stop if delta becomes
        smaller than ``mindelta``.
    error : str
        Error function to use.
    selective_stopping : int
        Selective stopping.
    return_history : bool
        Return error history as second return value.

    Returns
    -------
    history[best_iter] : None | array
        Winning kernel, or None if 0 is the best kernel.
    test_sse_history : list (only if ``return_history==True``)
        SSE for test data at each iteration.
    """
    delta_error_func = DELTA_ERROR_FUNC[error]
    error = ERROR_FUNC[error]
    n_stims, n_times = x.shape
    assert y.shape == (n_times,)

    h = np.zeros((n_stims, trf_length))

    # buffers
    y_error = y.copy()
    new_error = np.empty(h.shape)
    new_sign = np.empty(h.shape, np.int8)
    x_active = np.ones(n_stims, dtype=np.int8)

    # history
    best_test_error = np.inf
    history = []
    i_stim = i_time = delta_signed = None
    best_iteration = 0
    # pre-assign iterators
    for i_boost in range(999999):
        # evaluate current h
        e_test = error(y_error, test_index)
        e_train = error(y_error, train_index)
        step = BoostingStep(i_stim, i_time, delta_signed, e_test, e_train)
        history.append(step)

        # evaluate stopping conditions
        if e_test < best_test_error:
            best_test_error = e_test
            best_iteration = i_boost
        elif i_boost >= 2 and e_test > history[-2].e_test:
            if selective_stopping:
                if selective_stopping > 1:
                    n_bad = selective_stopping - 1
                    # only stop if the predictor overfits twice without intermittent improvement
                    undo = 0
                    for i in range(-2, -len(history), -1):
                        step = history[i]
                        if step.e_test > e_test:
                            break  # the error improved
                        elif step.i_stim == i_stim:
                            if step.e_test > history[i - 1].e_test:
                                # the same stimulus caused an error increase
                                if n_bad == 1:
                                    undo = i
                                    break
                                n_bad -= 1
                            else:
                                break
                else:
                    undo = -1

                if undo:
                    # revert changes
                    for i in range(-undo):
                        step = history.pop(-1)
                        h[step.i_stim, step.i_time] -= step.delta
                        update_error(y_error, x[step.i_stim], x_pads[step.i_stim], all_index, -step.delta, step.i_time + i_start)
                    step = history[-1]
                    # disable predictor
                    x_active[i_stim] = False
                    if not np.any(x_active):
                        break
                    new_error[i_stim, :] = np.inf
            # Basic
            # -----
            # stop the iteration if all the following requirements are met
            # 1. more than 10 iterations are done
            # 2. The testing error in the latest iteration is higher than that in
            #    the previous two iterations
            elif i_boost > 10 and e_test > history[-3].e_test:
                # print("error(test) not improving in 2 steps")
                break

        # generate possible movements -> training error
        generate_options(y_error, x, x_pads, x_active, train_index, i_start, delta_error_func, delta, new_error, new_sign)

        i_stim, i_time = np.unravel_index(np.argmin(new_error), h.shape)
        new_train_error = new_error[i_stim, i_time]
        delta_signed = new_sign[i_stim, i_time] * delta

        # If no improvements can be found reduce delta
        if new_train_error > step.e_train:
            delta *= 0.5
            if delta >= mindelta:
                i_stim = i_time = delta_signed = None
                # print("new delta: %s" % delta)
                continue
            else:
                # print("No improvement possible for training data")
                break

        # abort if we're moving in circles
        if step.delta and i_stim == step.i_stim and i_time == step.i_time and delta_signed == -step.delta:
            break

        # update h with best movement
        h[i_stim, i_time] += delta_signed
        update_error(y_error, x[i_stim], x_pads[i_stim], all_index, delta_signed, i_time + i_start)
    else:
        raise RuntimeError("Maximum number of iterations exceeded")
    # print('  (%i iterations)' % (i_boost + 1))

    # reverse changes after best iteration
    if best_iteration:
        for step in history[-1: best_iteration: -1]:
            if step.delta:
                h[step.i_stim, step.i_time] -= step.delta
    else:
        h = None

    if return_history:
        return h, [step.e_test for step in history]
    else:
        return h


def setup_workers(data, i_start, trf_length, delta, mindelta, error, selective_stopping):
    n_y, n_times = data.y.shape
    n_x, _ = data.x.shape

    y_buffer = RawArray('d', n_y * n_times)
    y_buffer[:] = data.y.ravel()
    x_buffer = RawArray('d', n_x * n_times)
    x_buffer[:] = data.x.ravel()
    x_pads_buffer = RawArray('d', n_x)
    x_pads_buffer[:] = data.x_pads

    job_queue = Queue(200)
    result_queue = Queue(200)

    args = (y_buffer, x_buffer, x_pads_buffer, n_y, n_times, n_x, data.cv_segments, i_start, trf_length, delta, mindelta, error, selective_stopping, job_queue, result_queue)
    for _ in range(CONFIG['n_workers']):
        process = Process(target=boosting_worker, args=args)
        process.start()

    return job_queue, result_queue


def boosting_worker(y_buffer, x_buffer, x_pads_buffer, n_y, n_times, n_x, cv_segments, i_start, trf_length, delta, mindelta, error, selective_stopping, job_queue, result_queue):
    if CONFIG['nice']:
        os.nice(CONFIG['nice'])

    y = np.frombuffer(y_buffer, np.float64, n_y * n_times).reshape((n_y, n_times))
    x = np.frombuffer(x_buffer, np.float64, n_x * n_times).reshape((n_x, n_times))
    x_pads = np.frombuffer(x_pads_buffer, np.float64, n_x)

    while True:
        y_i, seg_i = job_queue.get()
        if y_i == JOB_TERMINATE:
            return
        all_index, train_index, test_index = cv_segments[seg_i]
        h = boost(y[y_i], x, x_pads, all_index, train_index, test_index, i_start, trf_length, delta, mindelta, error, selective_stopping)
        result_queue.put((y_i, seg_i, h))


def put_jobs(queue, n_y, n_segs, stop):
    "Feed boosting jobs into a Queue"
    for job in product(range(n_y), range(n_segs)):
        queue.put(job)
        if stop.isSet():
            while not queue.empty():
                queue.get()
            break
    for _ in range(CONFIG['n_workers']):
        queue.put((JOB_TERMINATE, None))


def convolve(h, x, x_pads, h_i_start, segments=None, out=None):
    """h * x with time axis matching x

    Parameters
    ----------
    h : array, (n_stims, h_n_samples)
        H.
    x : array, (n_stims, n_samples)
        X.
    x_pads : array (n_stims,)
        Padding for x.
    h_i_start : int
        Time shift of the first sample of ``h``.
    segments : array (n_segments, 2)
        Data segments.
    out : array
        Buffer for predicted ``y``.
    """
    n_x, n_times = x.shape
    h_n_times = h.shape[1]
    if out is None:
        out = np.zeros(n_times)
    else:
        out.fill(0)

    if segments is None:
        segments = ((0, n_times),)

    # determine valid section of convolution (cf. _ndvar.convolve())
    h_i_max = h_i_start + h_n_times - 1
    out_start = max(0, h_i_start)
    out_stop = min(0, h_i_max)
    conv_start = max(0, -h_i_start)
    conv_stop = -h_i_start

    # padding
    h_pad = np.sum(h * x_pads[:, newaxis], 0)
    # padding for pre-
    pad_head_n_times = max(0, h_n_times + h_i_start)
    if pad_head_n_times:
        pad_head = np.zeros(pad_head_n_times)
        for i in range(min(pad_head_n_times, h_n_times)):
            pad_head[:pad_head_n_times - i] += h_pad[- i - 1]
    else:
        pad_head = None
    # padding for post-
    pad_tail_n_times = -min(0, h_i_start)
    if pad_tail_n_times:
        pad_tail = np.zeros(pad_tail_n_times)
        for i in range(pad_tail_n_times):
            pad_tail[i:] += h_pad[i]
    else:
        pad_tail = None

    for start, stop in segments:
        if pad_head is not None:
            out[start: start + pad_head_n_times] += pad_head
        if pad_tail is not None:
            out[stop - pad_tail_n_times: stop] += pad_tail

        out_index = slice(start + out_start, stop + out_stop)
        y_index = slice(conv_start, stop - start + conv_stop)
        for ind in range(n_x):
            out[out_index] += scipy.signal.convolve(h[ind], x[ind, start:stop])[y_index]

    return out


def evaluate_kernel(y, y_pred, error, i_skip, segments=None):
    """Fit quality statistics

    Parameters
    ----------
    y : array, (n_samples)
        Y.
    y_pred : array, (n_samples)
        Predicted Y.
    error : str
        Error metric.
    i_skip : int
        Skip this many samples for evaluating model fit.
    segments : array (n_segments, 2)
        Data segments.

    Returns
    -------
    r : float | array
        Pearson correlation.
    rank_r : float | array
        Spearman rank correlation.
    error : float | array
        Error corresponding to error_func.
    """
    # discard onset
    if i_skip:
        assert segments is None, "Not implemented"
        y = y[i_skip:]
        y_pred = y_pred[i_skip:]

    error_func = ERROR_FUNC[error]
    index = np.array(((0, len(y)),), np.int64)
    return (np.corrcoef(y, y_pred)[0, 1],
            spearmanr(y, y_pred)[0],
            error_func(y - y_pred, index))

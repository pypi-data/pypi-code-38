# Authors: Denis Engemann <denis.engemann@gmail.com>
#
# License: BSD (3-clause)
import logging

import numpy as np
from numpy.polynomial.legendre import legval
from scipy import linalg

import mne
from mne.bem import _fit_sphere
from mne.forward import _map_meg_channels
from mne.io.pick import pick_types, pick_channels
from mne.surface import _normalize_vectors


# mne 0.10 function
def map_meg_channels(inst, picks_good, picks_bad, mode):
    info_from = mne.pick_info(inst.info, picks_good, copy=True)
    info_to = mne.pick_info(inst.info, picks_bad, copy=True)
    return _map_meg_channels(info_from, info_to, mode=mode)


# private in 0.9.0 (Epochs method)
def get_channel_positions(self, picks=None):
    """Gets channel locations from info

    Parameters
    ----------
    picks : array-like of int | None
        Indices of channels to include. If None (default), all meg and eeg
        channels that are available are returned (bad channels excluded).
    """
    if picks is None:
        picks = pick_types(self.info, meg=True, eeg=True)
    chs = self.info['chs']
    pos = np.array([chs[k]['loc'][:3] for k in picks])
    n_zero = np.sum(np.sum(np.abs(pos), axis=1) == 0)
    if n_zero > 1:  # XXX some systems have origin (0, 0, 0)
        raise ValueError('Could not extract channel positions for '
                         '{} channels'.format(n_zero))
    return pos


def _calc_g(cosang, stiffness=4, num_lterms=50):
    """Calculate spherical spline g function between points on a sphere.

    Parameters
    ----------
    cosang : array-like of float, shape(n_channels, n_channels)
        cosine of angles between pairs of points on a spherical surface. This
        is equivalent to the dot product of unit vectors.
    stiffness : float
        stiffness of the spline.
    num_lterms : int
        number of Legendre terms to evaluate.

    Returns
    -------
    G : np.ndrarray of float, shape(n_channels, n_channels)
        The G matrix.
    """
    factors = [(2 * n + 1) / (n ** stiffness * (n + 1) ** stiffness *
                              4 * np.pi) for n in range(1, num_lterms + 1)]
    return legval(cosang, [0] + factors)


def _calc_h(cosang, stiffness=4, num_lterms=50):
    """Calculate spherical spline h function between points on a sphere.

    Parameters
    ----------
    cosang : array-like of float, shape(n_channels, n_channels)
        cosine of angles between pairs of points on a spherical surface. This
        is equivalent to the dot product of unit vectors.
    stiffness : float
        stiffness of the spline. Also referred to as `m`.
    num_lterms : int
        number of Legendre terms to evaluate.
    H : np.ndrarray of float, shape(n_channels, n_channels)
        The H matrix.
    """
    factors = [(2 * n + 1) /
               (n ** (stiffness - 1) * (n + 1) ** (stiffness - 1) * 4 * np.pi)
               for n in range(1, num_lterms + 1)]
    return legval(cosang, [0] + factors)


def _make_interpolation_matrix(pos_from, pos_to, alpha=1e-5):
    """Compute interpolation matrix based on spherical splines

    Implementation based on [1]

    Parameters
    ----------
    pos_from : np.ndarray of float, shape(n_good_sensors, 3)
        The positions to interpoloate from.
    pos_to : np.ndarray of float, shape(n_bad_sensors, 3)
        The positions to interpoloate.
    alpha : float
        Regularization parameter. Defaults to 1e-5.

    Returns
    -------
    interpolation : np.ndarray of float, shape(len(pos_from), len(pos_to))
        The interpolation matrix that maps good signals to the location
        of bad signals.

    References
    ----------
    [1] Perrin, F., Pernier, J., Bertrand, O. and Echallier, JF. (1989).
        Spherical splines for scalp potential and current density mapping.
        Electroencephalography Clinical Neurophysiology, Feb; 72(2):184-7.
    """

    pos_from = pos_from.copy()
    pos_to = pos_to.copy()

    # normalize sensor positions to sphere
    _normalize_vectors(pos_from)
    _normalize_vectors(pos_to)

    # cosine angles between source positions
    cosang_from = pos_from.dot(pos_from.T)
    cosang_to_from = pos_to.dot(pos_from.T)
    G_from = _calc_g(cosang_from)
    G_to_from, H_to_from = (f(cosang_to_from) for f in (_calc_g, _calc_h))

    if alpha is not None:
        G_from.flat[::len(G_from) + 1] += alpha

    C_inv = linalg.pinv(G_from)
    interpolation = G_to_from.dot(C_inv)
    return interpolation


def _make_interpolator(inst, bad_channels):
    """Find indexes and interpolation matrix to interpolate bad channels

    Parameters
    ----------
    inst : mne.io.Raw, mne.Epochs or mne.Evoked
        The data to interpolate. Must be preloaded.
    """
    logger = logging.getLogger(__name__)

    bads_idx = np.zeros(len(inst.ch_names), dtype=np.bool)
    goods_idx = np.zeros(len(inst.ch_names), dtype=np.bool)

    picks = pick_types(inst.info, meg=False, eeg=True, exclude=[])
    bads_idx[picks] = [inst.ch_names[ch] in bad_channels for ch in picks]
    goods_idx[picks] = True
    goods_idx[bads_idx] = False

    pos = get_channel_positions(inst, picks)

    # Make sure only EEG are used
    bads_idx_pos = bads_idx[picks]
    goods_idx_pos = goods_idx[picks]

    pos_good = pos[goods_idx_pos]
    pos_bad = pos[bads_idx_pos]

    # test spherical fit
    radius, center = _fit_sphere(pos_good, False)
    distance = np.sqrt(np.sum((pos_good - center) ** 2, 1))
    distance = np.mean(distance / radius)
    if np.abs(1. - distance) > 0.1:
        logger.warning('Your spherical fit is poor, interpolation results are '
                       'likely to be inaccurate.')

    logger.info('Computing interpolation matrix from {0} sensor '
                'positions'.format(len(pos_good)))

    interpolation = _make_interpolation_matrix(pos_good, pos_bad)

    return goods_idx, bads_idx, interpolation


def _interpolate_bads_eeg(epochs, bad_channels_by_epoch):
    """Interpolate bad channels per epoch

    Parameters
    ----------
    inst : mne.io.Raw, mne.Epochs or mne.Evoked
        The data to interpolate. Must be preloaded.
    bad_channels_by_epoch : list of list of str
        Bad channel names specified for each epoch. For example, for an Epochs
        instance containing 3 epochs: ``[['F1'], [], ['F3', 'FZ']]``
    """
    logger = logging.getLogger(__name__)

    if len(bad_channels_by_epoch) != len(epochs):
        raise ValueError("Unequal length of epochs (%i) and "
                         "bad_channels_by_epoch (%i)"
                         % (len(epochs), len(bad_channels_by_epoch)))

    interp_cache = {}
    for i, bad_channels in enumerate(bad_channels_by_epoch):
        if not bad_channels:
            continue

        # find interpolation matrix
        key = tuple(sorted(bad_channels))
        if key in interp_cache:
            goods_idx, bads_idx, interpolation = interp_cache[key]
        else:
            goods_idx, bads_idx, interpolation = interp_cache[key] \
                                = _make_interpolator(epochs, key)

        # apply interpolation
        logger.info('Interpolating %i sensors on epoch %i', bads_idx.sum(), i)
        epochs._data[i, bads_idx, :] = np.dot(interpolation,
                                              epochs._data[i, goods_idx, :])


def _interpolate_bads_meg(epochs, bad_channels_by_epoch, interp_cache):
    """Interpolate bad MEG channels per epoch

    Parameters
    ----------
    inst : mne.io.Raw, mne.Epochs or mne.Evoked
        The data to interpolate. Must be preloaded.
    bad_channels_by_epoch : list of list of str
        Bad channel names specified for each epoch. For example, for an Epochs
        instance containing 3 epochs: ``[['F1'], [], ['F3', 'FZ']]``
    interp_cache : dict
        Will be updated.

    Notes
    -----
    Based on mne 0.9.0 MEG channel interpolation.
    """
    logger = logging.getLogger(__name__)
    if len(bad_channels_by_epoch) != len(epochs):
        raise ValueError("Unequal length of epochs (%i) and "
                         "bad_channels_by_epoch (%i)"
                         % (len(epochs), len(bad_channels_by_epoch)))

    import time
    logger.debug("starting interpolation")
    t0 = time.time()

    # make sure bad_chs includes only existing channels
    all_chs = set(epochs.ch_names)
    bad_channels_by_epoch = [all_chs.intersection(chs) for chs in
                             bad_channels_by_epoch]

    # find needed interpolators
    sorted_bad_chs_by_epoch = [tuple(sorted(bad_channels)) for bad_channels in
                               bad_channels_by_epoch]
    needed = set(sorted_bad_chs_by_epoch)
    needed.discard(())
    n_keys = len(needed)
    if not n_keys:
        return
    bads = tuple(sorted(epochs.info['bads']))

    # make sure the cache is based on the correct channels
    if 'ch_names' not in interp_cache or interp_cache['ch_names'] != epochs.ch_names:
        interp_cache.clear()
        interp_cache['ch_names'] = epochs.ch_names

    # create interpolators
    make_interpolators(interp_cache, needed, bads, epochs)
    t1 = time.time()

    logger.debug("interpolate epochs")
    for i, key in enumerate(sorted_bad_chs_by_epoch):
        if not key:
            continue
        # apply interpolation
        picks_good, picks_bad, interpolation = interp_cache[bads, key]
        logger.info('Interpolating sensors %s on epoch %s', picks_bad, i)
        epochs._data[i, picks_bad, :] = interpolation.dot(epochs._data[i, picks_good, :])
    t2 = time.time()

    logger.debug("Interpolation took %s/%s seconds" % (t1 - t0, t2 - t1))


def make_interpolators(interp_cache, keys, bads, epochs):
    make = [k for k in keys if (bads, k) not in interp_cache]
    logger = logging.getLogger(__name__)
    logger.debug("Making %i of %i interpolators" % (len(make), len(keys)))
    for key in make:
        picks_good = pick_types(epochs.info, ref_meg=False, exclude=key)
        picks_bad = pick_channels(epochs.ch_names, key)
        interpolation = map_meg_channels(epochs, picks_good, picks_bad, 'accurate')
        interp_cache[bads, key] = picks_good, picks_bad, interpolation

# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>

import os
from warnings import catch_warnings, filterwarnings

from nose.tools import eq_
from numpy.testing import assert_array_equal, assert_array_almost_equal

import mne
from mne import pick_types

from eelbrain import load

from ...tests.test_data import assert_dataobj_equal
from eelbrain.testing import requires_mne_sample_data, file_path


FILTER_WARNING = 'The measurement information indicates a low-pass frequency of 40 Hz.'


@requires_mne_sample_data
def test_load_fiff_mne():
    data_path = mne.datasets.sample.data_path()
    fwd_path = os.path.join(data_path, 'MEG', 'sample', 'sample-ico-4-fwd.fif')
    evoked_path = os.path.join(data_path, 'MEG', 'sample',
                               'sample_audvis-no-filter-ave.fif')
    cov_path = os.path.join(data_path, 'MEG', 'sample', 'sample_audvis-cov.fif')
    mri_sdir = os.path.join(data_path, 'subjects')

    mne_evoked = mne.read_evokeds(evoked_path, 'Left Auditory')
    mne_fwd = mne.read_forward_solution(fwd_path)
    mne_fwd = mne.convert_forward_solution(mne_fwd, force_fixed=True, use_cps=True)
    cov = mne.read_cov(cov_path)

    picks = mne.pick_types(mne_evoked.info, 'mag')
    channels = [mne_evoked.ch_names[i] for i in picks]

    mne_evoked = mne_evoked.pick_channels(channels)
    mne_fwd = mne.pick_channels_forward(mne_fwd, channels)
    cov = mne.pick_channels_cov(cov, channels)

    mne_inv = mne.minimum_norm.make_inverse_operator(mne_evoked.info, mne_fwd,
                                                     cov, 0, None, True)

    mne_stc = mne.minimum_norm.apply_inverse(mne_evoked, mne_inv, 1., 'MNE')

    meg = load.fiff.evoked_ndvar(mne_evoked)
    inv = load.fiff.inverse_operator(mne_inv, 'ico-4', mri_sdir)
    stc = inv.dot(meg)
    assert_array_almost_equal(stc.get_data(('source', 'time')), mne_stc.data)

    fwd = load.fiff.forward_operator(mne_fwd, 'ico-4', mri_sdir)
    reconstruct = fwd.dot(stc)
    mne_reconstruct = mne.apply_forward(mne_fwd, mne_stc, mne_evoked.info)
    assert_array_almost_equal(reconstruct.get_data(('sensor', 'time')),
                              mne_reconstruct.data)


def test_load_fiff_sensor():
    umd_sqd_path = file_path('test_umd-raw.sqd')
    raw = mne.io.read_raw_kit(umd_sqd_path)

    sensor = load.fiff.sensor_dim(raw)
    eq_(sensor.sysname, 'KIT-UMD-3')


@requires_mne_sample_data
def test_load_fiff_from_raw():
    "Test loading data from a fiff raw file"
    data_path = mne.datasets.sample.data_path()
    meg_path = os.path.join(data_path, 'MEG', 'sample')
    raw_path = os.path.join(meg_path, 'sample_audvis_filt-0-40_raw.fif')
    evt_path = os.path.join(meg_path, 'sample_audvis_filt-0-40_raw-eve.fif')

    # load events
    ds = load.fiff.events(raw_path)
    eq_(ds['i_start'].x.dtype.kind, 'i')

    # test separate events
    ds_evt = load.fiff.events(events=evt_path)
    ds_evt.name = ds.name
    assert_dataobj_equal(ds_evt, ds)

    # add epochs as ndvar
    ds = ds.sub('trigger == 32')
    with catch_warnings():
        filterwarnings('ignore', message=FILTER_WARNING)
        ds_ndvar = load.fiff.add_epochs(ds, -0.1, 0.3, decim=10, data='mag',
                                        proj=False, reject=2e-12)
    meg = ds_ndvar['meg']
    eq_(meg.ndim, 3)
    data = meg.get_data(('case', 'sensor', 'time'))

    # compare with mne epochs
    with catch_warnings():
        filterwarnings('ignore', message=FILTER_WARNING)
        ds_mne = load.fiff.add_mne_epochs(ds, -0.1, 0.3, decim=10, proj=False,
                                          reject={'mag': 2e-12})
    epochs = ds_mne['epochs']
    # events
    assert_array_equal(epochs.events[:, 1], 0)
    assert_array_equal(epochs.events[:, 2], 32)
    # data
    picks = pick_types(epochs.info, meg='mag')
    mne_data = epochs.get_data()[:, picks]
    assert_array_equal(meg.sensor.names, [epochs.info['ch_names'][i] for i in picks])
    assert_array_equal(data, mne_data)
    assert_array_almost_equal(meg.time, epochs.times)

    # with proj
    with catch_warnings():
        filterwarnings('ignore', message=FILTER_WARNING)
        meg = load.fiff.epochs(ds, -0.1, 0.3, decim=10, data='mag', proj=True,
                               reject=2e-12)
        epochs = load.fiff.mne_epochs(ds, -0.1, 0.3, decim=10, proj=True,
                                      reject={'mag': 2e-12})
    picks = pick_types(epochs.info, meg='mag')
    mne_data = epochs.get_data()[:, picks]
    assert_array_almost_equal(meg.x, mne_data, 10)

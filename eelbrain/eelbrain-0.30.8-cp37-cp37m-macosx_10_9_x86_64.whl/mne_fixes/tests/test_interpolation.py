# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from numpy.testing import assert_array_equal, assert_array_almost_equal

from eelbrain import datasets
from eelbrain.mne_fixes import _interpolate_bads_meg
from eelbrain.testing import requires_mne_sample_data


@requires_mne_sample_data
def test_interpolation():
    "Test MNE channel interpolation by epoch"
    ds = datasets.get_mne_sample(sub=[0, 1, 2, 3])
    bads1 = ['MEG 0531', 'MEG 1321']
    bads3 = ['MEG 0531', 'MEG 2231']
    bads_list = [[], bads1, [], bads3]
    test_epochs = ds['epochs']
    epochs1 = test_epochs.copy()
    epochs3 = test_epochs.copy()

    _interpolate_bads_meg(test_epochs, bads_list, {})
    assert_array_equal(test_epochs._data[0], epochs1._data[0])
    assert_array_equal(test_epochs._data[2], epochs1._data[2])
    epochs1.info['bads'] = bads1
    epochs1.interpolate_bads(mode='accurate')
    assert_array_almost_equal(test_epochs._data[1], epochs1._data[1], 25)
    epochs3.info['bads'] = bads3
    epochs3.interpolate_bads(mode='accurate')
    assert_array_almost_equal(test_epochs._data[3], epochs3._data[3], 25)

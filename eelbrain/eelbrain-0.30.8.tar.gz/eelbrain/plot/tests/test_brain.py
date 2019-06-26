# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import sys

import numpy as np
import pytest

from eelbrain import datasets, plot, _info, NDVar
from eelbrain._wxgui.testing import hide_plots


@hide_plots
def test_plot_brain():
    """Test plot.brain plots"""
    if sys.platform.startswith('win'):
        pytest.xfail("Hangs on Appveyor")
    stc = datasets.get_mne_stc(True)

    # size
    b = plot.brain.brain(stc.source, hemi='rh', w=400, h=300, mask=False)
    assert b.screenshot().shape == (300, 400, 3)
    if sys.platform == 'linux':
        pytest.xfail("Brain.set_size() on Linux/Travis")
    b.set_size(200, 150)
    assert b.screenshot().shape == (150, 200, 3)
    b.close()
    # both hemispheres
    b = plot.brain.brain(stc.source, w=600, h=300, mask=False)
    assert b.screenshot().shape == (300, 600, 3)
    b.set_size(400, 150)
    assert b.screenshot().shape == (150, 400, 3)
    b.close()

    # plot shortcuts
    p = plot.brain.dspm(stc, mask=False)
    cb = p.plot_colorbar()
    cb.close()
    p.close()

    p = plot.brain.dspm(stc, hemi='lh', mask=False)
    cb = p.plot_colorbar()
    cb.close()
    p.close()

    p = plot.brain.cluster(stc, hemi='rh', views='parietal', mask=False)
    cb = p.plot_colorbar()
    cb.close()
    p.close()

    image = plot.brain.bin_table(stc, tstart=0.05, tstop=0.07, tstep=0.01, surf='white', mask=False)
    print(repr(image))
    print(image)

    # plot p-map
    pmap = NDVar(np.random.uniform(0, 1, stc.shape), stc.dims, _info.for_p_map(stc.info))
    p = plot.brain.p_map(pmap, stc, mask=False)
    cb = p.plot_colorbar()
    cb.close()
    p.close()

    # mask
    stcm = stc.mask(stc < 11)
    p = plot.brain.brain(stcm, mask=False)
    p.close()

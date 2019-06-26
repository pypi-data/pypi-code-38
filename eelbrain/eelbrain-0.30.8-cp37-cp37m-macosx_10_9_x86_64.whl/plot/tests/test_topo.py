# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from matplotlib.backend_bases import KeyEvent
import numpy as np
import pytest
import wx

from eelbrain import datasets, plot, testnd
from eelbrain._utils import IS_WINDOWS
from eelbrain.testing import requires_mne_sample_data
from eelbrain._wxgui.testing import hide_plots


def test_plot_topomap():
    "Test plot.Topomap"
    ds = datasets.get_uts(utsnd=True)
    topo = ds.eval('utsnd.summary(time=(0.075, 0.125))')

    p = plot.Topomap(topo, ds=ds)
    p.add_contour('V', 1, '#00FF00')
    p.close()
    p = plot.Topomap(topo, ds=ds, vmax=0.2, w=2)
    p.close()
    p = plot.Topomap(topo, 'A%B', ds=ds, axw=2)
    p.close()
    p = plot.Topomap(topo, ds=ds, sensorlabels=None)
    p.close()
    index = np.array([1, 3, 2])
    p = plot.Topomap(topo[index], '.case', nrow=1, axh=2, h=2.4, axtitle=index)
    p.close()


@requires_mne_sample_data
@hide_plots
def test_plot_topomap_mne():
    "Test plot.Topomap with MNE data"
    ds = datasets.get_mne_sample(sub=[0, 1], sns=True)
    p = plot.Topomap(ds['meg'].summary(time=(.1, .12)), proj='left')
    p.close()
    # grad
    ds = datasets.get_mne_sample(sub=[0], sns='grad')
    with pytest.raises(NotImplementedError), pytest.warns(RuntimeWarning):
        plot.Topomap('meg.sub(time=.1)', ds=ds)


@hide_plots
def test_plot_topo_butterfly():
    "Test plot.TopoButterfly"
    ds = datasets.get_uts(utsnd=True)

    # single row
    p = plot.TopoButterfly('utsnd', ds=ds)
    p.set_time(0.2)
    # t keypress on topomap
    x, y = p.topo_axes[0].transAxes.transform((.5, .5))
    event = KeyEvent('test', p.canvas, 't', x, y, wx.KeyEvent())
    p._on_key_press(event)
    p.close()

    p = plot.TopoButterfly('utsnd', ds=ds, vmax=0.2, w=6)
    p.close()

    # multiple rows
    p = plot.TopoButterfly('utsnd', 'A%B', ds=ds, w=6)
    if not IS_WINDOWS:
        assert (*p.figure.get_size_inches(),) == (6, 12)
    # t keypress on topomaps
    for ax in p.topo_axes:
        x, y = ax.transAxes.transform((.5, .5))
        event = KeyEvent('test', p.canvas, 't', x, y, wx.KeyEvent())
        p._on_key_press(event)
    p.close()

    p = plot.TopoButterfly('utsnd', mark=[1, 2], ds=ds)
    p.close()

    p = plot.TopoButterfly('utsnd', mark=['1', '2'], ds=ds)
    p.set_vlim(2)
    assert p.get_vlim() == (-2.0, 2.0)
    p.set_ylim(-1, 1)
    assert p.get_ylim() == (-1.0, 1.0)
    p.close()


@hide_plots
def test_plot_array():
    "Test plot.TopoArray"
    ds = datasets.get_uts(utsnd=True)
    p = plot.TopoArray('utsnd', ds=ds)
    assert repr(p) == "<TopoArray: utsnd>"
    p.set_topo_t(0, 0.2)
    p.close()
    p = plot.TopoArray('utsnd', ds=ds, vmax=0.2, w=2)
    p.close()
    p = plot.TopoArray('utsnd', 'A%B', ds=ds, axw=4)
    assert repr(p) == "<TopoArray: utsnd ~ A x B>"
    p.close()

    # results
    res = testnd.ttest_ind('utsnd', 'A', ds=ds, pmin=0.05, tstart=0.1, tstop=0.3, samples=2)
    p = plot.TopoArray(res)
    assert repr(p) == "<TopoArray: a0, a1, difference>"
    p.set_topo_t(0, 0.)
    p.close()

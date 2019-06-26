# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from eelbrain import datasets, Celltable, testnd
from eelbrain._stats import t_contrast
from eelbrain._stats.stats import t_1samp
from eelbrain._stats.t_contrast import TContrastRel

from nose.tools import eq_, assert_raises
import numpy as np
from numpy.testing import assert_equal, assert_array_equal


def test_t_contrast_parsing():
    "Test parsing of t-contrast expressions"
    y = np.arange(9.).reshape((3, 3))
    indexes = {'a': 0, 'b': 1, 'c': 2}

    contrast = "sum(a>c, b>c)"
    contrast_ = t_contrast.parse(contrast)
    eq_(contrast_, ('afunc', np.sum, (('comp', 'a', 'c'),
                                      ('comp', 'b', 'c'))))
    _, cells = t_contrast._t_contrast_rel_properties(contrast_)
    pc, mc = t_contrast._t_contrast_rel_expand_cells(cells, ('a', 'b', 'c'))
    data = t_contrast._t_contrast_rel_data(y, indexes, pc, mc)
    assert_equal(data['a'], np.arange(0., 3.))
    assert_equal(data['b'], np.arange(3., 6.))
    assert_equal(data['c'], np.arange(6., 9.))

    contrast = "sum(a>*, b>*)"
    contrast_ = t_contrast.parse(contrast)
    eq_(contrast_, ('afunc', np.sum, (('comp', 'a', '*'),
                                      ('comp', 'b', '*'))))
    _, cells = t_contrast._t_contrast_rel_properties(contrast_)
    pc, mc = t_contrast._t_contrast_rel_expand_cells(cells, ('a', 'b', 'c'))
    data = t_contrast._t_contrast_rel_data(y, indexes, pc, mc)
    assert_equal(data['a'], np.arange(0., 3.))
    assert_equal(data['b'], np.arange(3., 6.))
    assert_equal(data['*'], y.mean(0))

    assert_raises(ValueError, t_contrast._t_contrast_rel_expand_cells, cells,
                  ('a|c', 'b|c', 'c|c'))

    # test finding cells
    all_cells = (('fondue pot', 'brie'), ('fondue mix', 'brie'),
                 ('fondue pot', 'edam'), ('raclette', 'edam'))
    cells = (('* pot', '*'), ('fondue *', 'brie'))
    pc, mc = t_contrast._t_contrast_rel_expand_cells(cells, all_cells)
    eq_(pc, set(all_cells[:3]))
    eq_(mc, {('* pot', '*'): (('fondue pot', 'brie'), ('fondue pot', 'edam')),
             ('fondue *', 'brie'): (('fondue pot', 'brie'), ('fondue mix', 'brie'))})


def test_t_contrasts():
    "Test computation of various t-contrasts"
    ds = datasets.get_uts()
    ct = Celltable('uts', 'A % B', 'rm', ds=ds)
    y = ct.y.x
    out = np.empty(y.shape[1:])
    perm = np.arange(ds.n_cases)
    a1b1 = ct.data['a1', 'b1'].x
    a1b0 = ct.data['a1', 'b0'].x
    a0b1 = ct.data['a0', 'b1'].x
    a0b0 = ct.data['a0', 'b0'].x

    # simple t-test
    tgt = t_1samp(a1b0 - a0b0)
    c = TContrastRel("a1|b0 > a0|b0", ct.cells, ct.data_indexes)
    assert_equal(c.map(y), tgt)
    assert_equal(c(y, out, perm), tgt)
    out.fill(0)
    assert_equal(c(y, out, perm), tgt)
    c = TContrastRel("(a1|b0 > a0|b0)", ct.cells, ct.data_indexes)
    assert_equal(c.map(y), tgt)
    assert_equal(c(y, out, perm), tgt)
    out.fill(0)
    assert_equal(c(y, out, perm), tgt)

    # intersection
    tgt = np.min((t_1samp(a1b0 - a0b0), t_1samp(a1b1 - a0b1)), 0)
    c = TContrastRel("min(a1|b0 > a0|b0, a1|b1 > a0|b1)", ct.cells, ct.data_indexes)
    assert_equal(c.map(y), tgt)
    assert_equal(c(y, out, perm), tgt)
    out.fill(0)
    assert_equal(c(y, out, perm), tgt)

    # unary function
    tgt = np.abs(t_1samp(a1b0 - a0b0))
    c = TContrastRel("abs(a1|b0 > a0|b0)", ct.cells, ct.data_indexes)
    assert_equal(c.map(y), tgt)
    assert_equal(c(y, out, perm), tgt)
    out.fill(0)
    assert_equal(c(y, out, perm), tgt)

    # "VMod"
    tgt = t_1samp(a1b0 - a0b0) - np.abs(t_1samp(a1b1 - a0b1))
    c = TContrastRel("(a1|b0 > a0|b0) - abs(a1|b1 > a0|b1)", ct.cells,
                     ct.data_indexes)
    assert_equal(c.map(y), tgt)

    c = TContrastRel("subtract(a1|b0 > a0|b0, abs(a1|b1 > a0|b1))", ct.cells,
                     ct.data_indexes)
    assert_equal(c.map(y), tgt)
    assert_equal(c(y, out, perm), tgt)
    out.fill(0)
    assert_equal(c(y, out, perm), tgt)


def test_t_contrast_testnd():
    ds = datasets.get_uts()

    # binary function
    res = testnd.t_contrast_rel('uts', 'A', "a1>a0 - a0>a1", 'rm', ds=ds, tmin=4, samples=10)
    assert_equal(res.find_clusters()['p'], np.array([1, 1, 0.9, 0, 0.2, 1, 1, 0]))
    res_t = testnd.ttest_rel('uts', 'A', 'a1', 'a0', match='rm', ds=ds, tmin=2, samples=10)
    assert_array_equal(res.t.x, res_t.t.x * 2)
    assert_array_equal(res.clusters['tstart'], res_t.clusters['tstart'])
    assert_array_equal(res.clusters['tstop'], res_t.clusters['tstop'])
    assert_array_equal(res.clusters['v'], res_t.clusters['v'] * 2)

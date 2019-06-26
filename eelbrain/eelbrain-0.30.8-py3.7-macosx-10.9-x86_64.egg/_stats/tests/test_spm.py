# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
import pickle
from nose.tools import eq_
import numpy as np
from numpy.testing import assert_array_equal

from eelbrain import datasets
from eelbrain._stats.spm import LM, LMGroup


def test_lm():
    ds = datasets.get_uts()
    model = ds.eval("A*B*Y")
    coeffs = ds['uts'].ols(model)

    lm = LM('uts', 'A*B*Y', ds, 'effect')
    eq_(repr(lm), "<LM: uts ~ A + B + A x B + Y + A x Y + B x Y + A x B x Y>")
    for i, effect in enumerate(model.effects):
        assert_array_equal(lm.coefficient(effect.name).x, coeffs.x[i])


def test_random_lm():
    # dummy coding
    ds = datasets.get_uts()
    lms = []
    for i in range(5):
        ds['uts'].x += np.random.normal(0, 2, ds['uts'].shape)
        lms.append(LM('uts', 'A*B*Y', ds))
    rlm = LMGroup(lms)
    eq_(repr(rlm), '<LMGroup: uts ~ A + B + A x B + Y + A x Y + B x Y + A x B x Y, n=5>')

    # coefficients
    ds = rlm.coefficients_dataset(('A', 'A x B'))
    eq_(ds['term'].cells, ('A', 'A x B'))

    # tests
    res = rlm.column_ttest('A x B', samples=100, pmin=0.05, mintime=0.025)
    eq_(res.clusters.n_cases, 1)

    # effect coding
    ds = datasets.get_uts()
    lms = []
    for i in range(5):
        ds['uts'].x += np.random.normal(0, 2, ds['uts'].shape)
        lms.append(LM('uts', 'A*B*Y', ds, 'effect'))
    rlm = LMGroup(lms)
    res = rlm.column_ttest('A x B', samples=100, pmin=0.05, mintime=0.025)
    eq_(res.clusters.n_cases, 6)

    # persistence
    rlm_p = pickle.loads(pickle.dumps(rlm, pickle.HIGHEST_PROTOCOL))
    eq_(rlm_p.dims, rlm.dims)

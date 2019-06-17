import numpy as np
from mne import Transform
from mne.io.constants import FIFF


def dig_equal(dig1, dig2, kind=None):
    if kind is not None:
        dig1 = (d for d in dig1 if d['kind'] in kind)
        dig2 = (d for d in dig2 if d['kind'] in kind)
    return all(np.array_equal(a['r'], b['r']) for a, b in zip(dig1, dig2))


def hsp_equal(dig1, dig2):
    return dig_equal(dig1, dig2, (FIFF.FIFFV_POINT_EXTRA,))


def mrk_equal(dig1, dig2):
    return dig_equal(dig1, dig2, (FIFF.FIFFV_POINT_HPI,))


def trans_equal(trans1, trans2):
    assert isinstance(trans1, Transform)
    assert isinstance(trans2, Transform)
    return all(trans1['from'] == trans2['from'], trans1['to'] == trans2['from'],
               np.array_equal(trans1['trans'], trans2['trans']))

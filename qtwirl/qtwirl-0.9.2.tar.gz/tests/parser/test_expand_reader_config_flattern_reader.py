# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

import alphatwirl

from qtwirl._parser.readerconfig import expand_reader_config

##__________________________________________________________________||
RoundLog = mock.Mock()

tblcfg_dict1 = dict(
    key_name=('jet_pt', ),
    key_binning=(RoundLog(0.1, 100), ),
    key_index=('*', ),
)

tblcfg_dict2 = dict(
    key_name=('met', ),
    key_binning=(RoundLog(0.1, 100), ),
)

selection_cfg_dict = dict(All=('ev: ev.njets[0] > 4', ))
selection_cfg_str = 'ev: ev.njets[0] > 4'

scribbler1 = mock.MagicMock()
scribbler2 = mock.Mock()

##__________________________________________________________________||
params = [

    #
    pytest.param(None, None, id='none'),

    #
    ##
    pytest.param(dict(reader=[]), None, id='reader-empty'),
    pytest.param(dict(reader=[None]), None, id='reader-none'),
    pytest.param(dict(reader=[None, None]), None, id='reader-none'),

    ##
    pytest.param(
        dict(reader=scribbler1),
        dict(reader=scribbler1),
        id='reader-reader'),
    pytest.param(
        dict(reader=[scribbler1]),
        [dict(reader=scribbler1)],
        id='reader-reader'),
    pytest.param(
        dict(reader=[scribbler1, None]),
        [dict(reader=scribbler1)],
        id='reader-reader'),
    pytest.param(
        dict(reader=[scribbler1, scribbler2]),
        [dict(reader=scribbler1), dict(reader=scribbler2)],
        id='reader-reader'),
    pytest.param(
        dict(reader=[scribbler1, None, scribbler2]),
        [dict(reader=scribbler1), dict(reader=scribbler2)],
        id='reader-reader'),

    #
    ##
    pytest.param([ ], [ ], id='list-empty'),
    pytest.param([None], [ ], id='list-none'),
    pytest.param([None, None], [ ], id='list-none'),

    ##
    pytest.param([dict(reader=[])], [ ], id='list-reader'),
    pytest.param([dict(reader=[]), dict(reader=[])], [ ], id='list-reader'),

    pytest.param(
        [dict(reader=scribbler1)],
        [dict(reader=scribbler1)],
        id='list-reader'),
    pytest.param(
        [dict(reader=[scribbler1])],
        [dict(reader=scribbler1)],
        id='list-reader'),
    pytest.param(
        [dict(reader=[scribbler1, None])],
        [dict(reader=scribbler1)],
        id='list-reader'),
    pytest.param(
        [dict(reader=[scribbler1]), None],
        [dict(reader=scribbler1)],
        id='list-reader'),

    #
    pytest.param(
        [dict(reader=[scribbler1, scribbler2])],
        [dict(reader=scribbler1), dict(reader=scribbler2)],
        id='two-readers'
    ),
    pytest.param(
        [dict(reader=[scribbler1]), dict(reader=scribbler2)],
        [dict(reader=scribbler1), dict(reader=scribbler2)],
        id='two-readers'
    ),
]

@pytest.mark.parametrize('arg, expected', params)
def test_expand_reader_config(arg, expected):
    assert expected == expand_reader_config(arg)

##__________________________________________________________________||

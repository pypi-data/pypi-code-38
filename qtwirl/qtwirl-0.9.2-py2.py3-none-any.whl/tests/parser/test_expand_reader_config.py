# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.readerconfig import expand_reader_config
from qtwirl._parser.tableconfig import complete_table_cfg
from qtwirl._parser.selectionconfig import complete_selection_cfg, _wrap_cfg

##__________________________________________________________________||
from alphatwirl.summary import WeightCalculatorOne

def eq(self, other):
    return isinstance(other, self.__class__)
WeightCalculatorOne.__eq__ = eq

##__________________________________________________________________||
RoundLog = mock.Mock()

tblcfg_dict1 = dict(
    key_name='jet_pt',
    key_binning=RoundLog(0.1, 100),
    key_index='*',
)

tblcfg_dict2 = dict(
    key_name='met',
    key_binning=RoundLog(0.1, 100),
)

tblcfg_dict1_completed = dict(complete_table_cfg(tblcfg_dict1))
tblcfg_dict2_completed = dict(complete_table_cfg(tblcfg_dict2))

selection_cfg_dict = dict(All=('ev: ev.njets[0] > 4', ))
selection_cfg_str = 'ev: ev.njets[0] > 4'

selection_cfg_dict_completed = dict(complete_selection_cfg(_wrap_cfg(selection_cfg_dict)))
selection_cfg_str_completed = dict(complete_selection_cfg(_wrap_cfg(selection_cfg_str)))

scribbler1 = mock.Mock()

##__________________________________________________________________||
params = [
    # pytest.param(
    #     dict(), dict(table_cfg=dict(expanded_table_cfg=dict())), id='empty-dict'
    # ),
    pytest.param(
        dict(), dict(table_cfg=complete_table_cfg(dict())), id='empty-dict'
    ),
    pytest.param(
        [ ], [ ], id='empty-list'
    ),
    pytest.param(
        dict(tblcfg_dict1),
        dict(table_cfg=tblcfg_dict1_completed),
        id='dict-short'
    ),
    pytest.param(
        dict(table_cfg=tblcfg_dict1),
        dict(table_cfg=tblcfg_dict1_completed),
        id='dict-full'
    ),
    pytest.param(
        [tblcfg_dict1],
        [dict(table_cfg=tblcfg_dict1_completed)],
        id='list-with-one-dict'
    ),
    pytest.param(
        [tblcfg_dict1, tblcfg_dict2],
        [
            dict(table_cfg=tblcfg_dict1_completed),
            dict(table_cfg=tblcfg_dict2_completed),
        ],
        id='two-table-cfgs-short'
    ),
    pytest.param(
        [
            dict(table_cfg=tblcfg_dict1),
            dict(tblcfg_dict2),
        ],
        [
            dict(table_cfg=tblcfg_dict1_completed),
            dict(table_cfg=tblcfg_dict2_completed),
        ],
        id='two-table-cfgs-full-short'
    ),
    pytest.param(
        [
            dict(table_cfg=tblcfg_dict1),
            dict(table_cfg=tblcfg_dict2),
        ],
        [
            dict(table_cfg=tblcfg_dict1_completed),
            dict(table_cfg=tblcfg_dict2_completed),
        ],
        id='two-table-cfgs-full'
    ),
    pytest.param(
        [
            dict(selection_cfg=selection_cfg_dict),
            tblcfg_dict1,
        ],
        [
            dict(selection_cfg=selection_cfg_dict_completed),
            dict(table_cfg=tblcfg_dict1_completed),
        ],
        id='one-selection-dict-one-table'
    ),
    pytest.param(
        [
            dict(selection_cfg=selection_cfg_str),
            tblcfg_dict1,
        ],
        [
            dict(selection_cfg=selection_cfg_str_completed),
            dict(table_cfg=tblcfg_dict1_completed),
        ],
        id='one-selection-str-one-table'
    ),
    pytest.param(
        dict(selection_cfg=selection_cfg_dict),
        dict(selection_cfg=selection_cfg_dict_completed),
        id='one-selection-dict'
    ),
    pytest.param(
        dict(selection_cfg=selection_cfg_str),
        dict(selection_cfg=selection_cfg_str_completed),
        id='one-selection-str'
    ),
    pytest.param(
        [
            dict(reader=scribbler1),
            tblcfg_dict1,
        ],
        [
            dict(reader=scribbler1),
            dict(table_cfg=tblcfg_dict1_completed),
        ],
        id='one-scribbler-one-table'
    ),
]

@pytest.mark.parametrize('arg, expected', params)
def test_expand_reader_config(arg, expected):
    actual = expand_reader_config(arg)
    from pprint import pprint
    pprint(actual)
    pprint(expected)
    assert expected == actual

##__________________________________________________________________||

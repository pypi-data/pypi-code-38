# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.selectionconfig import expand_selection_cfg

##__________________________________________________________________||
params = [
        (
            'ev: ev.njets[0] > 4',
            dict(
                default_cfg_stack=[dict(selection_cfg=dict(store_file=True))]
            ),
            dict(selection_cfg=dict(
                condition='ev: ev.njets[0] > 4',
                count=False,
                store_file=True,
                file_path='tbl_selection_count.txt'
            ))
        ),
]

@pytest.mark.parametrize('cfg, shared, expected', params)
def test_expand(cfg, shared, expected):
    actual = expand_selection_cfg(cfg, shared)
    print(expected)
    print(actual)
    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||

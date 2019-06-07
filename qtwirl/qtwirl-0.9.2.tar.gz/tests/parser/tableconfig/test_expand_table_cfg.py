# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.tableconfig import expand_table_cfg

##__________________________________________________________________||
def mock_complete_table_cfg(cfg):
    return dict(mock_complete=cfg)

@pytest.fixture(autouse=True)
def monkeypatch_complete_table_cfg(monkeypatch):
    from qtwirl._parser import tableconfig
    monkeypatch.setattr(tableconfig, 'complete_table_cfg', mock_complete_table_cfg)

##__________________________________________________________________||
params = [
        (dict(key_name='jet_pt'),
         dict(default_cfg_stack=[dict(table_cfg=dict(store_file=True))]),
         dict(table_cfg=dict(mock_complete=dict(key_name='jet_pt', store_file=True)))
        ),
]

@pytest.mark.parametrize('cfg, shared, expected', params)
def test_expand(cfg, shared, expected):
    actual = expand_table_cfg(cfg, shared)
    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||

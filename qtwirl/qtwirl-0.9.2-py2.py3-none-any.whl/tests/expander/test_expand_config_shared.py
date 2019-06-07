# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import _expand_config

##__________________________________________________________________||
@pytest.fixture()
def mock_expand_one_dict(monkeypatch):
    def ret(cfg, shared):
        shared['modified'] = True

    import qtwirl._parser.expander as module
    monkeypatch.setattr(module, '_expand_one_dict', ret)
    return ret

def test_not_share_shared(mock_expand_one_dict):
    cfg = [dict(A=1)]
    shared = dict(modified=False)
    _expand_config(cfg, shared)
    assert dict(modified=False) == shared

##__________________________________________________________________||

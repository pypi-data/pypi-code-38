# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import _expand_config

##__________________________________________________________________||
def test_expand_config_none():
    cfg = None
    expected = None
    actual = _expand_config(cfg)
    assert expected == actual

##__________________________________________________________________||
@pytest.fixture()
def mock_expand_one_dict(monkeypatch):
    ret = mock.Mock()
    import qtwirl._parser.expander as module
    monkeypatch.setattr(module, '_expand_one_dict', ret)
    return ret

@pytest.mark.parametrize('cfg', [dict(), dict(A=1)])
@pytest.mark.parametrize('func_ret', [None, [], {}, dict(A=1), [dict(B=2, C=3)]])
def test_expand_config_one_dict(cfg, func_ret, mock_expand_one_dict):
    if func_ret:
        expected = func_ret
    else:
        expected = None
    mock_expand_one_dict.return_value = func_ret
    actual = _expand_config(cfg)
    assert expected == actual

##__________________________________________________________________||
@pytest.mark.parametrize(
    'cfg, func_side_eff, expected', [
        ([], [], []),
        ([None],[None], []),
        ([None],[dict(X=1)], []),
        ([None],[[]], []),
        ([None],[[dict(X=1)]], []),
        ([None],[[dict(X=1), dict(Y=2)]], []),
        ([dict(A=1)], [None], []),
        ([dict(A=1)], [dict(X=1)], [dict(X=1)]),
        ([dict(A=1)], [[]], []),
        ([dict(A=1)], [[dict(X=1)]], [dict(X=1)]),
        ([dict(A=1)], [[dict(X=1), dict(Y=2)]], [dict(X=1), dict(Y=2)]),
        ([dict(A=1)], [[dict(X=1), dict(Y=2), None]], [dict(X=1), dict(Y=2)]),

        ([dict(A=1), None], [None, dict(X=1)], []),
        ([dict(A=1), None], [dict(X=1), dict(X=1)], [dict(X=1)]),
        ([dict(A=1), None], [[], dict(X=1)], []),
        ([dict(A=1), None], [[dict(X=1)], dict(X=1)], [dict(X=1)]),
        ([dict(A=1), None], [[dict(X=1), dict(Y=2)], dict(X=1)], [dict(X=1), dict(Y=2)]),
        ([dict(A=1), None], [[dict(X=1), dict(Y=2), None], dict(X=1)], [dict(X=1), dict(Y=2)]),

        ([dict(A=1), dict(B=2)], [None, None], []),
        ([dict(A=1), dict(B=2)], [dict(X=1), None], [dict(X=1)]),
        ([dict(A=1), dict(B=2)], [dict(X=1), dict(Y=2)], [dict(X=1), dict(Y=2)]),
        ([dict(A=1), dict(B=2)], [dict(X=1), [dict(Y=2), dict(Z=3)]], [dict(X=1), dict(Y=2), dict(Z=3)]),
        ([dict(A=1), dict(B=2)], [dict(X=1), [dict(Y=2), dict(Z=3), None]], [dict(X=1), dict(Y=2), dict(Z=3)]),

    ]
)
def test_expand_config_list(cfg, func_side_eff, expected, mock_expand_one_dict):
    mock_expand_one_dict.side_effect = func_side_eff
    actual = _expand_config(cfg)
    assert expected == actual

##__________________________________________________________________||

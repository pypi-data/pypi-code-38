# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import config_expander

##__________________________________________________________________||
def expand_abc_cfg(cfg):
    return dict(abc_cfg=dict(expanded=cfg))

def expand_def_cfg(cfg):
    return dict(def_cfg=dict(expanded=cfg))

##__________________________________________________________________||
def test_simple():
    expand_func_map = {'abc_cfg': expand_abc_cfg}
    config_keys = [ ]
    default_config_key = 'abc_cfg'
    expand_config = config_expander(
        expand_func_map=expand_func_map,
        config_keys=config_keys,
        default_config_key=default_config_key
    )

    assert {'abc_cfg': {'expanded': {'A': 1}}} == expand_config(dict(A=1))

##__________________________________________________________________||
def test_set_default_not_overridden(caplog):
    mock_set_default = mock.Mock()
    expand_func_map = {
        'abc_cfg': expand_abc_cfg,
        'set_default' : mock_set_default, # give 'set_default'
    }
    config_keys = [ ]
    default_config_key = 'abc_cfg'

    #
    with caplog.at_level(logging.INFO):
        expand_config = config_expander(
            expand_func_map=expand_func_map,
            config_keys=config_keys,
            default_config_key=default_config_key)

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'INFO'
    assert 'expander' in caplog.records[0].name
    assert '"set_default" is in' in caplog.records[0].msg

    shared = expand_config.keywords['shared']
    assert mock_set_default == shared['expand_func_map']['set_default']

##__________________________________________________________________||
@pytest.mark.parametrize('default_cfg_dict', [None, dict(A=1)])
def test_default_cfg_dict(default_cfg_dict):
    expand_config = config_expander(default_cfg_dict=default_cfg_dict)
    shared = expand_config.keywords['shared']
    if default_cfg_dict is None:
        assert [{}] == shared['default_cfg_stack']
    else:
        assert [default_cfg_dict] == shared['default_cfg_stack']

##__________________________________________________________________||
def test_func_apply_default():
    expand_config = config_expander()
    shared = expand_config.keywords['shared']
    func_apply_default = shared['func_apply_default']
    assert 'apply_default' == func_apply_default.__name__

##__________________________________________________________________||
def test_wrap():
    mock_set_default = mock.Mock()
    expand_func_map = {
        'abc_cfg': expand_abc_cfg,
        'def_cfg': expand_def_cfg,
    }
    config_keys = ['xyz_cfg']
    default_config_key = 'abc_cfg'

    #
    expand_config = config_expander(
        expand_func_map=expand_func_map,
        config_keys=config_keys,
        default_config_key=default_config_key)

    assert 'expand_config' == expand_config.__name__
    assert  'expand a config' in expand_config.__doc__

##__________________________________________________________________||

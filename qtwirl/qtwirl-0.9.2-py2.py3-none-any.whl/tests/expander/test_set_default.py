# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import pytest

from qtwirl._parser.expander import _set_default, _wrap_default_cfg

##__________________________________________________________________||
params = [
    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        'abc_cfg', # default_config_key
        dict(abc_cfg=dict(A=1)), # cfg
        dict(abc_cfg=dict(A=1)), # expected
        id='simple'
    ),

    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        'abc_cfg', # default_config_key
        dict(A=1), # cfg
        dict(abc_cfg=dict(A=1)), # expected
        id='wrapped-with-default'
    ),

    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        'abc_cfg', # default_config_key
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=1)), # cfg
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=1)), # expected
        id='two-items-in-cfg'
    ),

    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        'abc_cfg', # default_config_key
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=1), xyz_cfg=dict(X=1)), # cfg
        dict(abc_cfg=dict(abc_cfg=dict(A=1), def_cfg=dict(D=1), xyz_cfg=dict(X=1))), # expected
        id='extra-item-wrapped-with-default'
    ),

    # default_config_key: None
    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        None, # default_config_key
        dict(abc_cfg=dict(A=1)), # cfg
        dict(abc_cfg=dict(A=1)), # expected
        id='default-none'
    ),

    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        None, # default_config_key
        dict(A=1), # cfg
        dict(A=1), # expected
        id='default-none'
    ),

    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        None, # default_config_key
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=1)), # cfg
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=1)), # expected
        id='default-none'
    ),

    pytest.param(
        ['abc_cfg', 'def_cfg'], # config_keys
        None, # default_config_key
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=1), xyz_cfg=dict(X=1)), # cfg
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=1), xyz_cfg=dict(X=1)), # expected
        id='default-none'
    ),

]

param_names = 'config_keys, default_config_key, cfg, expected'

@pytest.mark.parametrize(param_names, params)
def test_set_default(config_keys, default_config_key, cfg, expected):
    default_cfg_stack = [ ]
    shared = dict(
        config_keys=config_keys,
        default_config_key=default_config_key,
        default_cfg_stack=default_cfg_stack
    )

    _set_default(cfg, shared)
    assert [expected] == default_cfg_stack

@pytest.mark.parametrize(param_names, params)
def test_wrap_default_cfg(config_keys, default_config_key, cfg, expected):
    assert expected == _wrap_default_cfg(cfg, config_keys, default_config_key)

##__________________________________________________________________||

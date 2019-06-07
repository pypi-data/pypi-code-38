# Tai Sakuma <tai.sakuma@gmail.com>
import sys
import functools
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import config_expander

##__________________________________________________________________||
params = [
    pytest.param(
        dict(),
        set([]),
        id='empty'),

    pytest.param(
        dict(expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg}),
        set(['abc_cfg']),
        id='empty-config-keys'),

    pytest.param(
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=['def_cfg']
        ),
        set(['abc_cfg', 'def_cfg']),
        id='default-none'),

    pytest.param(
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=['def_cfg'], default_config_key='abc_cfg'
        ),
        set(['abc_cfg', 'def_cfg']),
        id='default-in-list'),

    pytest.param(
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=['def_cfg'], default_config_key='xyz_cfg'
        ),
        set(['abc_cfg', 'def_cfg', 'xyz_cfg']),
        id='default-not-in-list'),
]

@pytest.mark.parametrize('kwargs, expected', params)
def test_config_expander_config_keys(
        kwargs, expected) :
    """test if config_keys are correctly initialized

    """
    expected.add('set_default')
    expand_config = config_expander(**kwargs)
    actual_shared = expand_config.keywords['shared']
    actual = actual_shared['config_keys']
    assert expected == actual

##__________________________________________________________________||

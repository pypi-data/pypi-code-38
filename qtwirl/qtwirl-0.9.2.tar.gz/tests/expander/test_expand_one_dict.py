# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import pytest

from qtwirl._parser.expander import _expand_one_dict

##__________________________________________________________________||
params = [
    pytest.param(
        dict(abc_cfg=dict(A=1)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(abc_cfg=dict(expanded=dict(A=1))),
        id='simple'
    ),

    pytest.param(
        dict(A=1), # without config key, e.g, 'abc_cfg'
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(abc_cfg=dict(expanded=dict(A=1))),
        id='default'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)), # 'xyz_cfg' is not a config key
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(abc_cfg=dict(expanded=dict(xyz_cfg=dict(A=1)))),
        id='default'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)), # 'xyz_cfg' is a config key
        dict(
            config_keys=['abc_cfg', 'xyz_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(xyz_cfg=dict(A=1)),
        id='no-expansion'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key=None, # default is None
        ),
        dict(xyz_cfg=dict(A=1)),
        id='no-default'
    ),

    pytest.param(
        dict(A=1),
        dict(
            config_keys=['abc_cfg', 'xyz_cfg'],
            default_config_key='xyz_cfg',
        ),
        dict(xyz_cfg=dict(A=1)), # not expanded
        id='default-no-expansion'
    ),

    pytest.param(
        dict(A=1),
        dict(
            config_keys=['abc_cfg', 'def_cfg'],
            default_config_key='def_cfg',
        ),
        dict(def_cfg=dict(expanded=dict(A=1))),
        id='no-shared-option' # expand_def_cfg() doesn't take `shared`
    ),

]

def expand_abc_cfg(cfg, shared):
    return dict(abc_cfg=dict(expanded=cfg))

def expand_def_cfg(cfg): # doesn't take shared
    return dict(def_cfg=dict(expanded=cfg))

@pytest.mark.parametrize('cfg, shared, expected', params)
def test_expand_one_dict(cfg, shared, expected):
    shared['expand_func_map'] = {
        'abc_cfg': expand_abc_cfg,
        'def_cfg': expand_def_cfg,
        }
    actual = _expand_one_dict(cfg, shared)
    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||
params = [
    pytest.param(
        dict(abc_cfg=dict(A=1)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
            expand_func_map={'abc_cfg': expand_abc_cfg},
        ),
        dict(abc_cfg=dict(expanded=dict(A=1))), # not applied, only expanded
        id='with-expand-func'
    ),

    pytest.param(
        dict(abc_cfg=dict(A=1)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
            expand_func_map={ },
        ),
        dict(abc_cfg=dict(shared_applied=dict(A=1))),  # not expanded, only applied
        id='without-expand-func'
    ),

    pytest.param(
        dict(abc_cfg=dict(A=1)),
        dict(
            config_keys=[ ],
            default_config_key=None,
            expand_func_map={ },
        ),
        dict(abc_cfg=dict(shared_applied=dict(A=1))), # not applied, only expanded
        id='no-default'
    ),

    pytest.param(
        dict(abc_cfg=dict(A=1), xyz_cfg=dict(A=1)),
        dict(
            config_keys=[ ],
            default_config_key=None,
            expand_func_map={ },
        ),
        dict(abc_cfg=dict(A=1), xyz_cfg=dict(A=1)), # not applied, or expanded
        id='two-items'
    ),

]

def mock_apply_default_for_all_keys(cfg, shared):
    ret = cfg.copy()
    if 'abc_cfg' in ret:
        ret['abc_cfg'] = dict(shared_applied=ret['abc_cfg'])
    return ret

@pytest.fixture()
def monkeypatch_apply_default_for_all_keys(monkeypatch):
    import qtwirl._parser.expander as module
    monkeypatch.setattr(module, '_apply_default_for_all_keys', mock_apply_default_for_all_keys)
    return

@pytest.mark.parametrize('cfg, shared, expected', params)
def test_expand_one_dict_apply(cfg, shared, expected, monkeypatch_apply_default_for_all_keys):
    actual = _expand_one_dict(cfg, shared)
    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||

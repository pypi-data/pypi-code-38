# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import pytest

from qtwirl._parser.expander import _apply_default_for_all_keys

##__________________________________________________________________||
params = [

    pytest.param(
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=2), set_default=dict(H=22)),
        dict(
            default_cfg_stack=[
                dict(abc_cfg=dict(A=5, B=3, C=10), def_cfg=dict(D=5, E=3)),
                dict(abc_cfg=dict(B=2)),
                dict(set_default=dict(G=20)),
            ],
        ),
        dict(abc_cfg=dict(A=1, B=2, C=10), def_cfg=dict(D=2, E=3), set_default=dict(H=22)),
        id='simple'
    ),

    pytest.param(
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=2), set_default=dict(H=22)),
        dict(),
        dict(abc_cfg=dict(A=1), def_cfg=dict(D=2), set_default=dict(H=22)),
        id='no-default-cfg-stack'
    ),

]

param_names = 'cfg, shared, expected'

@pytest.mark.parametrize(param_names, params)
def test_apply_default_for_all_keys(cfg, shared, expected):
    assert expected == _apply_default_for_all_keys(cfg, shared)

##__________________________________________________________________||

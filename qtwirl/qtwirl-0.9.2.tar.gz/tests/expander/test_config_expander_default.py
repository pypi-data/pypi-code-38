# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.expander import config_expander

##__________________________________________________________________||
def expand_abc_cfg(cfg, shared):
    key = 'abc_cfg'
    cfg = shared['func_apply_default'](key, cfg)
    return {key: dict(expanded=cfg)}

##__________________________________________________________________||
@pytest.fixture()
def expand_config():
    expand_func_map = {
        'abc_cfg': expand_abc_cfg,
    }
    config_keys = ['def_cfg']
    default_config_key = 'abc_cfg'

    ret = config_expander(
        expand_func_map=expand_func_map,
        config_keys=config_keys,
        default_config_key=default_config_key
    )
    return ret

##__________________________________________________________________||
params = [
    (
        [
            dict(
                set_default=dict(
                    abc_cfg=dict(A=5, C=4),
                    def_cfg=dict(D=2, E=9),
                )),
            dict(A=1, B=2)
        ],
        [
            dict(abc_cfg=dict(expanded=dict(A=1, B=2, C=4)))
        ]
    ),

    (
        [
            dict(set_default=dict(A=5, C=4)),
            dict(A=1, B=2)
        ],
        [
            dict(abc_cfg=dict(expanded=dict(A=1, B=2, C=4)))
        ]
    ),

    (
        [
            dict(set_default=dict(abc_cfg=dict(B=3, C=2, E=8))),
            dict(set_default=dict(A=5, C=4)),
            dict(A=1, B=2),
        ],
        [
            dict(abc_cfg=dict(expanded=dict(A=1, B=2, C=4, E=8)))
        ]
        )
]

@pytest.mark.parametrize('cfg, expected', params)
def test_default(cfg, expected, expand_config):
    assert expected == expand_config(cfg)

##__________________________________________________________________||
def test_default_no_memory(expand_config):

    cfg = [
        dict(set_default=dict(C=4)),
        dict(A=1)
    ]

    expected = [
        dict(abc_cfg=dict(expanded=dict(A=1, C=4)))
    ]

    assert expected == expand_config(cfg)

    cfg = [
        dict(A=1)
    ]

    expected = [
        dict(abc_cfg=dict(expanded=dict(A=1)))
        # must not be dict(abc_cfg=dict(expanded=dict(A=1, C=4)))
    ]

    assert expected == expand_config(cfg)

##__________________________________________________________________||

# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.tableconfig import compose_tbl_filename_from_config

##__________________________________________________________________||
params = [
    pytest.param(
        [dict(key_out_name=('var1', 'var2'))],
        { }, 'tbl.var1.var2.txt', id='simple'),
    pytest.param(
        [dict(key_out_name=('var1', 'var2'), file_name_prefix='def')],
        { }, 'def.var1.var2.txt', id='simple'),
    pytest.param(
        [dict(key_out_name=('var1', 'var2'))],
        dict(default=dict(file_name_prefix='abc')),
        'abc.var1.var2.txt', id='default'),
    pytest.param(
        [dict(key_out_name=('var1', 'var2'), file_name_prefix='def')],
        dict(default=dict(file_name_prefix='abc')),
        'def.var1.var2.txt', id='override'),

    pytest.param(
        [dict(key_out_name=('var1', 'var2'), key_index=(1, 2))],
        dict(
            default=dict(
                file_name_prefix='abc',
                file_name_suffix='csv',
                file_name_var_separator='#',
                file_name_idx_separator='=',
            )),
        'abc#var1=1#var2=2.csv', id='default-all'),

    pytest.param(
        [dict(
            key_out_name=('var1', 'var2'),
            key_index=(1, 2),
            file_name_prefix='def',
            file_name_suffix='dat',
            file_name_var_separator='+',
            file_name_idx_separator='&',
        )],
        dict(
            default=dict(
                file_name_prefix='abc',
                file_name_suffix='csv',
                file_name_var_separator='#',
                file_name_idx_separator='=',
            )),
        'def+var1&1+var2&2.dat', id='default-all-override'),
]

@pytest.mark.parametrize('args, kwargs, expected', params)
def test_complete(args, kwargs, expected):
    actual = compose_tbl_filename_from_config(*args, **kwargs)
    assert expected == actual

##__________________________________________________________________||

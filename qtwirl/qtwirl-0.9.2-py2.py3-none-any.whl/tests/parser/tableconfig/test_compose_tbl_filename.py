# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.tableconfig import compose_tbl_filename

##__________________________________________________________________||
params = [
    pytest.param([( )], { }, 'tbl.txt', id='empty'),
    pytest.param(
        [('var1', 'var2', 'var3')], { },
        'tbl.var1.var2.var3.txt',
        id='no-indices'),
    pytest.param(
        [('var1', 'var2', 'var3')],
        dict(key_indices=(1, None, 2)),
        'tbl.var1-1.var2.var3-2.txt',
        id='simple'),
    pytest.param(
        [('var1', 'var2', 'var3')],
        dict(key_indices=(1, None, 2), prefix='tbl_Sum'),
        'tbl_Sum.var1-1.var2.var3-2.txt',
        id='prefix'),
    pytest.param(
        [('var1', 'var2', 'var3')],
        dict(key_indices=(1, None, 2), suffix='hdf5'),
        'tbl.var1-1.var2.var3-2.hdf5',
        id='suffix'),
    pytest.param(
        [('var1', 'var2', 'var3')],
        dict(key_indices=(1, None, '*')),
        'tbl.var1-1.var2.var3-w.txt',
        id='star'),
    pytest.param(
        [('var1', 'var2', 'var3', 'var4', 'var5')],
        dict(key_indices=(1, None, '*', '(*)', '\\1')),
        'tbl.var1-1.var2.var3-w.var4-wp.var5-b1.txt',
        id='backref'),
    pytest.param(
        [('var1', 'var2', 'var3', 'var4', 'var5')],
        dict(key_indices=(1, None, '*', '(*)', '\\1'), var_separator='#'),
        'tbl#var1-1#var2#var3-w#var4-wp#var5-b1.txt',
        id='var-separator'),
    pytest.param(
        [('var1', 'var2', 'var3', 'var4', 'var5')],
        dict(key_indices=(1, None, '*', '(*)', '\\1'), idx_separator='#'),
        'tbl.var1#1.var2.var3#w.var4#wp.var5#b1.txt',
        id='idx-separator'),
]

@pytest.mark.parametrize('args, kwargs, expected', params)
def test_complete(args, kwargs, expected):
    actual = compose_tbl_filename(*args, **kwargs)
    assert expected == actual

##__________________________________________________________________||

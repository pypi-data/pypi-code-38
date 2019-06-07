# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.selectionconfig import complete_selection_cfg, _wrap_cfg

##__________________________________________________________________||
params = [

    #
    (
        dict(condition='ev: ev.njets[0] > 4'),
        dict(condition='ev: ev.njets[0] > 4',
             count=False, store_file=False)
    ),
    (
        dict(condition=dict(All=('ev: ev.njets[0] > 4', ))),
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=False, store_file=False)
    ),

    #
    (
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True),
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_path='tbl_selection_count.txt')
    ),

    #
    (
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_dir='out'),
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_dir='out',
             file_path='out/tbl_selection_count.txt')
    ),

    #
    (
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_name='tbl_given-filename.txt'),
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_name='tbl_given-filename.txt',
             file_path='tbl_given-filename.txt')
    ),

    #
    (
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_dir='out',
             file_name='tbl_given-filename.txt'),
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_dir='out',
             file_name='tbl_given-filename.txt',
             file_path='out/tbl_given-filename.txt')
    ),

    #
    (
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_dir='out',
             file_name='tbl_given-filename-1.txt',
             file_path='abc/def/tbl_given-filename-2.txt'),
        dict(condition=dict(All=('ev: ev.njets[0] > 4', )),
             count=True, store_file=True,
             file_dir='out',
             file_name='tbl_given-filename-1.txt',
             file_path='abc/def/tbl_given-filename-2.txt'),
    ),

]

@pytest.mark.parametrize('arg, expected', params)
def test_complete(arg, expected):
    actual = complete_selection_cfg(arg)
    assert expected == actual
    assert arg is not actual

##__________________________________________________________________||
params = [
    (
        'ev: ev.njets[0] > 4',
        dict(condition='ev: ev.njets[0] > 4'),
    ),
    (
        dict(condition='ev: ev.njets[0] > 4'),
        dict(condition='ev: ev.njets[0] > 4'),
    ),
    (
        dict(All=('ev: ev.njets[0] > 4', )),
        dict(condition=dict(All=('ev: ev.njets[0] > 4', ))),
    ),
]

@pytest.mark.parametrize('arg, expected', params)
def test_wrap_cfg(arg, expected):
    actual = _wrap_cfg(arg)
    assert expected == actual
    if expected != actual:
        assert arg is not actual

##__________________________________________________________________||

# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.tableconfig import complete_table_cfg

from alphatwirl.summary import Count, WeightCalculatorOne


def eq(self, other):
    return isinstance(other, self.__class__)
WeightCalculatorOne.__eq__ = eq


##__________________________________________________________________||
class MockSummary2:
    pass

class MockBinning:
    pass

defaultWeight = WeightCalculatorOne()
binning1 = MockBinning()
binning2 = MockBinning()

##__________________________________________________________________||
params = [

    ## no key
    pytest.param(
        dict(),
        dict(
            key_name=(),
            key_index=None,
            key_binning=None,
            key_out_name=(),
            val_name=None,
            val_index=None,
            agg_class=Count,
            agg_name=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='no-key-empty-dict'
    ),
    pytest.param(
        dict(key_name=( ), key_binning=( )),
        dict(
            key_name=(),
            key_index=None,
            key_binning=(),
            key_out_name=(),
            val_name=None,
            val_index=None,
            agg_class=Count,
            agg_name=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='no-key-empty-key'
    ),

    ## one key
    pytest.param(
        dict(
            key_name='met_pt',
        ),
        dict(
            key_name=('met_pt',),
            key_index=None,
            key_binning=None,
            key_out_name=('met_pt',),
            val_name=None,
            val_index=None,
            agg_class=Count,
            agg_name=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='one-key-no-tuple'
    ),
    pytest.param(
        dict(
            key_name='met_pt',
            key_binning=binning1,
        ),
        dict(
            key_name=('met_pt',),
            key_index=None,
            key_binning=(binning1, ),
            key_out_name=('met_pt',),
            val_name=None,
            val_index=None,
            agg_class=Count,
            agg_name=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='one-key-one-bin-no-tuple'
    ),
    pytest.param(
        dict(
            key_name='met_pt',
            key_index=1,
            key_binning=binning1,
            key_out_name='met',
        ),
        dict(
            key_name=('met_pt',),
            key_index=(1, ),
            key_binning=(binning1, ),
            key_out_name=('met',),
            val_name=None,
            val_index=None,
            agg_class=Count,
            agg_name=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='one-key-idx-bin-out-no-tuple'
    ),
    pytest.param(
        dict(
            key_name=('met_pt', ),
            key_binning=(binning1, ),
        ),
        dict(
            key_name=('met_pt',),
            key_index=None,
            key_binning=(binning1, ),
            key_out_name=('met_pt',),
            val_name=None,
            val_index=None,
            agg_class=Count,
            agg_name=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='one-key-tuple'
    ),

    ## summary class
    pytest.param(
        dict(
            key_name=( ),
            key_binning=( ),
            agg_class=MockSummary2,
        ),
        dict(
            key_name=(),
            key_index=None,
            key_binning=(),
            key_out_name=(),
            val_name=None,
            val_index=None,
            agg_class=MockSummary2,
            agg_name=(),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-empty-key-empty-val'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=None,
            val_index=None,
            agg_class=MockSummary2,
            agg_name=(),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-keys-empty-vals'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name=('val1', ),
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', ),
            val_index=None,
            agg_class=MockSummary2,
            agg_name=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-keys-one-val-tuple'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name=('val1', ),
            val_index=('*', ),
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', ),
            val_index=('*', ),
            agg_class=MockSummary2,
            agg_name=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-keys-one-val-idx-tuple'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name=('val1', 'val2'),
            agg_class=MockSummary2,
            agg_name=('agg1', ),
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', 'val2'),
            val_index=None,
            agg_class=MockSummary2,
            agg_name=('agg1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-one-agg-tuple'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name=('val1', 'val2'),
            agg_class=MockSummary2,
            agg_name='agg1',
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', 'val2'),
            val_index=None,
            agg_class=MockSummary2,
            agg_name=('agg1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-one-agg-no-tuple'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name='val1',
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', ),
            val_index=None,
            agg_class=MockSummary2,
            agg_name=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-keys-one-val-no-tuple'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name='val1',
            val_index='*',
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', ),
            val_index=('*', ),
            agg_class=MockSummary2,
            agg_name=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-keys-one-val-idx-no-tuple'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name=('val1', 'val2'),
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', 'val2'),
            val_index=None,
            agg_class=MockSummary2,
            agg_name=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-keys-2-vals'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            key_index=(None, 1),
            val_name=('val1', 'val2'),
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=(None, 1),
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', 'val2'),
            val_index=None,
            agg_class=MockSummary2,
            agg_name=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-2-keys-2-vals-key-indices'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            val_name=('val1', 'val2'),
            agg_class=MockSummary2,
            val_index=(2, None),
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=None,
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', 'val2'),
            val_index=(2, None),
            agg_class=MockSummary2,
            agg_name=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-2-keys-2-vals-val-indices'
    ),
    pytest.param(
        dict(
            key_name=('key1', 'key2'),
            key_binning=(binning1, binning2),
            key_index=(None, 1),
            val_name=('val1', 'val2'),
            val_index=(2, 3),
            agg_class=MockSummary2,
        ),
        dict(
            key_name=('key1', 'key2'),
            key_index=(None, 1),
            key_binning=(binning1, binning2),
            key_out_name=('key1', 'key2'),
            val_name=('val1', 'val2'),
            val_index=(2, 3),
            agg_class=MockSummary2,
            agg_name=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
            store_file=False,
        ),
        id='summary-class-2-keys-2-vals-key-indices-val-indices'
    ),
]

@pytest.mark.parametrize('arg, expected', params)
def test_complete(arg, expected):
    actual = complete_table_cfg(arg)
    assert expected == actual
    assert arg is not actual

##__________________________________________________________________||

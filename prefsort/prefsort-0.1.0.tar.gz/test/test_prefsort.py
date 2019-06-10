
import pytest
import random
import pandas as pd

from prefsort import prefsorted


def test_trivial():

    seq = list('abcdefgh')
    random.shuffle(seq)

    assert prefsorted(seq) == seq


def test_docs():
    seq = list('abcde')

    seq2 = prefsorted(seq, 'c b')
    assert seq2 == ['c', 'b', 'a', 'd', 'e']

    seq2 = prefsorted(seq, 'c b', reverse=True)
    assert seq2 == ['a', 'd', 'e', 'c', 'b']


def test_basic():

    seq = list('abcdefgh')
    random.shuffle(seq)
    rest = list(seq)[:]
    rest.remove('g')
    rest.remove('e')
    rest.remove('b')

    assert prefsorted(seq, 'g e b') == list('geb') + rest
    assert prefsorted(seq, ['g', 'e', 'b']) == list('geb') + rest


def test_reverse():

    seq = list('abcdefgh')
    random.shuffle(seq)
    rest = seq[:]
    rest.remove('g')
    rest.remove('e')
    rest.remove('b')

    assert prefsorted(seq, 'g e b', reverse=True) == rest + list('geb')
    assert prefsorted(seq, ['g', 'e', 'b'], reverse=True) == rest + list('geb')


def test_pandas():
    df = pd.DataFrame({'a': [1, 2], 'b': [2, 3], 'c': [3, 4],
                       'd': [9, 19], 'e': [23, 23]})
    df = df.reindex(columns=prefsorted(df.columns, 'd b'))
    assert list(df.columns[:2]) == list('db')
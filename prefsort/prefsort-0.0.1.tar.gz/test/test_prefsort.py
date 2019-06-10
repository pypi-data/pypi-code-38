
import pytest
import random

from prefsort import prefsorted


def test_trivial():

    seq = list('abcdefgh')
    random.shuffle(seq)

    assert prefsorted(seq) == seq


def test_docs():
    seq = list('abcde')
    random.shuffle(seq)

    seq2 = prefsorted(seq, 'c b')
    assert seq2[0] == 'c'
    assert seq2[1] == 'b'
    assert set(seq2) == set(seq)


def test_basic():

    seq = list('abcdefgh')
    random.shuffle(seq)
    rest = seq[:]
    rest.remove('g')
    rest.remove('e')
    rest.remove('b')


    assert prefsorted(seq, 'g e b') == list('geb') + rest
    assert prefsorted(seq, ['g', 'e', 'b']) == list('geb') + rest
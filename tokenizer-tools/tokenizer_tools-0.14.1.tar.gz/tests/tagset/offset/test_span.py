import collections

from tokenizer_tools.tagset.offset.span import Span


def test_repr_():
    span = Span(0, 9, 'entity')
    assert repr(span) == "Span(0, 9, 'entity')"


def test_eq_():
    a = Span(0, 1, 'entity')
    b = Span(0, 1, 'entity')

    assert a == b

    c = Span(0, 2, 'entity')

    assert a != c


def test_hash_():
    a = Span(0, 1, 'entity')
    assert isinstance(a, collections.Hashable)


def test_init_():
    # TODO: check init checker
    pass

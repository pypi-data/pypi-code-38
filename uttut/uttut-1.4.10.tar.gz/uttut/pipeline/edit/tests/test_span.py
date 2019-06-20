from ..span import Span


def test_normal():
    start = 10
    end = 15
    span = Span(start, end)
    assert start == span.start
    assert end == span.end


def test_all_equal():
    assert Span(10, 15) == Span(10, 15)


def test_different_type():
    assert (10, 15) != Span(10, 15)


def test_different_start():
    assert Span(10, 15) != Span(9, 15)


def test_different_end():
    assert Span(10, 15) != Span(10, 11)


def test_str():
    span = Span(10, 15)
    assert "(10, 15)" == str(span)


def test_repr():
    span = Span(10, 15)
    assert "Span(10, 15)" == repr(span)

from tokenizer_tools.tagset.offset.span import Span
from tokenizer_tools.tagset.offset.span_set import SpanSet


def test_check_match():
    span_set = SpanSet()
    span_set.append(Span(1, 2, 'entity', '春'))
    span_set.append(Span(2, 3, 'entity', '秋'))
    assert span_set.check_match('赛春秋')[0] == True

    span_set = SpanSet()
    span_set.append(Span(1, 2, 'entity', '春'))
    span_set.append(Span(4, 6, 'entity', '秋天'))
    assert span_set.check_match('赛春秋赛秋天')[0] == True

    span_set = SpanSet()
    span_set.append(Span(1, 4, 'entity', '赛春秋'))
    span_set.append(Span(2, 3, 'entity', '春'))
    assert span_set.check_match('赛赛春秋')[0] == True

    span_set = SpanSet()
    span_set.append(Span(1, 4, 'entity', '赛春秋'))
    span_set.append(Span(2, 3, 'entity', '春'))
    check_result = span_set.check_match('不不不不')
    assert check_result[0] == False
    assert check_result[1] == [Span(1, 4, 'entity', '赛春秋'), Span(2, 3, 'entity', '春')]


def test_check_overlap():
    span_set = SpanSet()
    span_set.append(Span(1, 2, 'entity'))
    span_set.append(Span(2, 3, 'entity'))
    assert span_set.check_overlap()[0] == True

    span_set = SpanSet()
    span_set.append(Span(1, 2, 'entity'))
    span_set.append(Span(4, 6, 'entity'))
    assert span_set.check_overlap()[0] == True

    span_set = SpanSet()
    span_set.append(Span(1, 4, 'entity'))
    span_set.append(Span(2, 3, 'entity'))
    check_result = span_set.check_overlap()
    assert check_result[0] == False
    assert check_result[1] == [(Span(1, 4, 'entity'), Span(2, 3, 'entity'))]


def test_eq_():
    a = SpanSet()
    a.append(Span(1, 2, 'entity'))
    a.append(Span(2, 3, 'entity'))

    b = SpanSet()
    b.append(Span(1, 2, 'entity'))
    b.append(Span(2, 3, 'entity'))

    assert a == b

    c = SpanSet()  # empty SpanSet

    assert a != c

    d = SpanSet()  # same with `a` but different span order
    d.append(Span(2, 3, 'entity'))
    d.append(Span(1, 2, 'entity'))

    assert a == d

    e = SpanSet()  # same with `a` but different span order
    e.append(Span(0, 1, 'entity'))
    e.append(Span(1, 2, 'entity'))

    assert a != e

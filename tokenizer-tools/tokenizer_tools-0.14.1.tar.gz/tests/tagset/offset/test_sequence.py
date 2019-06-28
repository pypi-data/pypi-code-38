from tokenizer_tools.tagset.offset.sequence import Sequence
from tokenizer_tools.tagset.offset.span import Span


def test_check_span_set():
    seq = Sequence("王小明在北京的清华大学读书。")
    seq.span_set.append(Span(0, 3, 'PERSON', '王小明'))
    seq.span_set.append(Span(4, 6, 'GPE', '北京'))
    seq.span_set.append(Span(7, 11, 'ORG', '清华大学'))

    assert seq.check_span_set()
    
    seq = Sequence("来一首蓝泽雨的歌。")
    seq.span_set.append(Span(3, 6, '歌手名', '蓝泽雨'))
    seq.span_set.append(Span(5, 6, '歌曲名', '雨'))

    assert not seq.check_span_set()


def test_eq_():
    a = Sequence("text")

    b = Sequence("text")

    assert a == b

    c = Sequence("other_text")

    assert a != c

    d = Sequence('text')
    d.span_set.append(Span(0, 1, 'entity'))

    e = Sequence('text')
    e.span_set.append(Span(0, 1, 'entity'))

    assert d == e

    f = Sequence('text')
    f.span_set.append(Span(0, 2, 'entity'))

    assert d != f

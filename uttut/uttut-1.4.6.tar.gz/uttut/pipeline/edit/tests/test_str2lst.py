import pytest

from ..replacement import ReplacementGroup
from ..span import SpanGroup
from uttut.pipeline.edit import str2lst, lst2str


test_cases = [
    pytest.param(
        '我想要喝200元的珍奶10杯',
        ['我', '想要', '喝', '200元', '的', '珍奶', '10杯'],
        SpanGroup.add_all(
            [(0, 1), (1, 3), (3, 4), (4, 8), (8, 9), (9, 11), (11, 14)]),
        id='jieba',
    ),
    pytest.param(
        '我想要喝 200 元的珍奶 10 杯',
        ['我', '想要', '喝', ' ', '200', ' ', '元', '的', '珍奶', ' ', '10', ' ', '杯'],
        SpanGroup.add_all(
            [(0, 1), (1, 3), (3, 4), (4, 5), (5, 8), (8, 9), (9, 10),
             (10, 11), (11, 13), (13, 14), (14, 16), (16, 17), (17, 18)]),
        id='jieba with space',
    ),
    pytest.param(
        "I'vebeentoJapan.",
        ["I", "'", "ve", "been", "to", "Japan", "."],
        SpanGroup.add_all(
            [(0, 1), (1, 2), (2, 4), (4, 8), (8, 10), (10, 15), (15, 16)]),
        id='nltk punct after str2tr',
    ),
    pytest.param(
        "I'vebeentoJapan.",
        ["I've", "been", "to", "Japan", "."],
        SpanGroup.add_all(
            [(0, 4), (4, 8), (8, 10), (10, 15), (15, 16)]),
        id='nltk after str2tr',
    ),
]


@pytest.mark.parametrize("input_str,tokens,span_group,", test_cases)
def test_forward_apply(input_str, tokens, span_group):
    output = str2lst.apply(input_str, span_group)
    assert tokens == output


@pytest.mark.parametrize("input_str,tokens,span_group,", test_cases)
def test_backward_apply(input_str, tokens, span_group):
    output = lst2str.apply(tokens, span_group)
    assert input_str == output


def test_incompatible_str2lst():
    with pytest.raises(ValueError):
        str2lst.apply('薄餡亂入', SpanGroup.add_all([(0, 1), (1, 2)]))


@pytest.mark.parametrize(
    'input_lst,span_group',
    [
        pytest.param(['薄餡', '亂入'], SpanGroup.add_all([(0, 1)]), id='length'),
        pytest.param(['我', '想要', '喝', '多多綠'],
                     SpanGroup.add_all([(0, 1), (1, 3), (3, 5), (5, 8)]), id='element'),
    ],
)
def test_incompatible_lst2str(input_lst, span_group):
    with pytest.raises(ValueError):
        lst2str.apply(input_lst, span_group)


@pytest.mark.parametrize("input_str,tokens,span_group,", test_cases)
def test_gen_span_group(input_str, tokens, span_group):
    output = str2lst.gen_span_group(input_str, tokens)
    assert span_group == output


@pytest.mark.parametrize(
    'input_str,tokens',
    [
        pytest.param('我想要喝200元的珍奶10杯', ['薄餡', '亂入'], id='zh_all_mismatch'),
        pytest.param("I've been to Japan.", ["I", "'", "ve", "been", "to", "Japan", "."],
                     id='us lack of space'),
    ],
)
def test_gen_span_group_fail(input_str, tokens):
    with pytest.raises(ValueError, match='input_str and tokens are not compatible'):
        str2lst.gen_span_group(input_str, tokens)


@pytest.mark.parametrize(
    "input_str,tokens,replacement_group",
    [
        pytest.param(
            '我想要喝200元的珍奶10杯',
            ['我', '想要', '喝', '200元', '的', '珍奶', '10杯'],
            ReplacementGroup.add_all([]),
            id='jieba',
        ),
        pytest.param(
            '我想要喝 200 元的珍奶 10 杯',
            ['我', '想要', '喝', ' ', '200', ' ', '元', '的', '珍奶', ' ', '10', ' ', '杯'],
            ReplacementGroup.add_all([]),
            id='jieba with space',
        ),
        pytest.param(
            "I've been to Japan.",
            ["I", "'", "ve", "been", "to", "Japan", "."],
            ReplacementGroup.add_all([(4, 5, ''), (9, 10, ''), (12, 13, '')]),
            id='nltk punct True',
        ),
        pytest.param(
            "I've been to Japan.",
            ["I've", "been", "to", "Japan", "."],
            ReplacementGroup.add_all([(4, 5, ''), (9, 10, ''), (12, 13, '')]),
            id='nltk punct False',
        ),
    ],
)
def test_gen_replacement_group(input_str, tokens, replacement_group):
    output = str2lst.gen_replacement_group(input_str, tokens)
    assert replacement_group == output


@pytest.mark.parametrize(
    'input_str,tokens',
    [
        pytest.param('我想要喝200元的珍奶10杯', ['薄餡', '亂入'], id='zh_all_mismatch'),
        pytest.param('我想要喝珍奶', ['我', '想要', '喝', '多多綠'], id='zh_part_mismatch'),
        pytest.param('我想要喝珍奶', ['珍奶', '我', '想要', '喝'], id='zh_different_order'),
    ],
)
def test_gen_replacement_group_fail(input_str, tokens):
    with pytest.raises(ValueError, match='input_str and tokens are not compatible'):
        str2lst.gen_replacement_group(input_str, tokens)

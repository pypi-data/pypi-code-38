import pytest

from ..replacement import ReplacementGroup
from uttut.pipeline.edit import str2str


test_cases = [
    pytest.param(
        '我想要喝200元的珍奶10杯',
        ReplacementGroup.add_all([(4, 7, '_int_'), (11, 13, '_int_')]),
        '我想要喝_int_元的珍奶_int_杯',
        ReplacementGroup.add_all([(4, 9, '200'), (13, 18, '10')]),
        id='modify',
    ),
    pytest.param(
        '我想喝珍奶',
        ReplacementGroup.add_all([(0, 0, '其實'), (0, 1, '妳'), (1, 1, '不'),
                                  (3, 5, '多多綠'), (5, 5, '對吧！')]),
        '其實妳不想喝多多綠對吧！',
        ReplacementGroup.add_all([(0, 2, ''), (2, 3, '我'), (3, 4, ''),
                                  (6, 9, '珍奶'), (9, 12, '')]),
        id='insert',
    ),
    pytest.param(
        '我不想喝珍奶',
        ReplacementGroup.add_all([(1, 2, '')]),
        '我想喝珍奶',
        ReplacementGroup.add_all([(1, 1, '不')]),
        id='delete',
    ),
    pytest.param(
        '這個句子沒有改變',
        ReplacementGroup.add_all([]),
        '這個句子沒有改變',
        ReplacementGroup.add_all([]),
        id='identity',
    ),
]


@pytest.mark.parametrize(
    "input_str,forward_replacements,output_str,inverse_replacements",
    test_cases,
)
def test_forward_apply(input_str, forward_replacements, output_str, inverse_replacements):
    output = str2str.apply(input_str, forward_replacements)
    assert output_str == output


@pytest.mark.parametrize(
    "input_str,forward_replacements,output_str,inverse_replacements",
    test_cases,
)
def test_backward_apply(input_str, forward_replacements, output_str, inverse_replacements):
    output = str2str.apply(output_str, inverse_replacements)
    assert input_str == output


@pytest.mark.parametrize(
    "input_str,forward_replacements,output_str,inverse_replacements",
    test_cases,
)
def test_forward_inverse(input_str, forward_replacements, output_str, inverse_replacements):
    output = str2str.inverse(input_str, forward_replacements)
    assert inverse_replacements == output


@pytest.mark.parametrize(
    "input_str,forward_replacements,output_str,inverse_replacements",
    test_cases,
)
def test_backward_inverse(input_str, forward_replacements, output_str, inverse_replacements):
    output = str2str.inverse(output_str, inverse_replacements)
    assert forward_replacements == output

import pytest

from ..replacement import ReplacementGroup
from uttut.pipeline.edit import lst2lst


test_cases = [
    pytest.param(
        list('我想要喝200元的珍奶10杯'),
        ReplacementGroup.add_all([(4, 7, list('_int_')), (11, 13, list('_int_'))]),
        list('我想要喝_int_元的珍奶_int_杯'),
        ReplacementGroup.add_all([(4, 9, list('200')), (13, 18, list('10'))]),
        id='modify',
    ),
    pytest.param(
        list('我想喝珍奶'),
        ReplacementGroup.add_all([(0, 0, list('其實')), (0, 1, ['妳']), (1, 1, ['不']),
                                  (3, 5, list('多多綠')), (5, 5, list('對吧！'))]),
        list('其實妳不想喝多多綠對吧！'),
        ReplacementGroup.add_all([(0, 2, []), (2, 3, ['我']), (3, 4, []),
                                  (6, 9, list('珍奶')), (9, 12, [])]),
        id='insert',
    ),
    pytest.param(
        list('我不想喝珍奶'),
        ReplacementGroup.add_all([(1, 2, [])]),
        list('我想喝珍奶'),
        ReplacementGroup.add_all([(1, 1, ['不'])]),
        id='delete',
    ),
    pytest.param(
        ['這個', '句子', '沒有', '改變'],
        ReplacementGroup.add_all([]),
        ['這個', '句子', '沒有', '改變'],
        ReplacementGroup.add_all([]),
        id='identity',
    ),
]


@pytest.mark.parametrize(
    "input_lst,forward_replacements,output_lst,inverse_replacements",
    test_cases,
)
def test_forward_apply(input_lst, forward_replacements, output_lst, inverse_replacements):
    output = lst2lst.apply(input_lst, forward_replacements)
    assert output_lst == output


@pytest.mark.parametrize(
    "input_lst,forward_replacements,output_lst,inverse_replacements",
    test_cases,
)
def test_backward_apply(input_lst, forward_replacements, output_lst, inverse_replacements):
    output = lst2lst.apply(output_lst, inverse_replacements)
    assert input_lst == output


@pytest.mark.parametrize(
    "input_lst,forward_replacements,output_lst,inverse_replacements",
    test_cases,
)
def test_forward_inverse(input_lst, forward_replacements, output_lst, inverse_replacements):
    output = lst2lst.inverse(input_lst, forward_replacements)
    assert inverse_replacements == output


@pytest.mark.parametrize(
    "input_lst,forward_replacements,output_lst,inverse_replacements",
    test_cases,
)
def test_backward_inverse(input_lst, forward_replacements, output_lst, inverse_replacements):
    output = lst2lst.inverse(output_lst, inverse_replacements)
    assert forward_replacements == output

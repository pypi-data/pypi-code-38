import pytest

from ..replacement import ReplacementGroup
from ..span import SpanGroup
from ..label_propagation import (
    propagate_by_replacement_group,
    reduce_by_span_group,
    expand_by_span_group,
)


test_cases = [
    pytest.param(
        [1, 1, 1, 0, 0, 3, 0, 2, 2],
        ReplacementGroup.add_all([(0, 3, 'a'), (5, 6, 'abc'), (7, 9, 'abcd')]),
        [1, 0, 0, 3, 3, 3, 0, 2, 2, 2, 2],
        ReplacementGroup.add_all([(0, 1, 'abc'), (3, 6, 'a'), (7, 11, 'ab')]),
        id='str-modify',
    ),
    pytest.param(
        [1, 1, 1, 0, 0, 3, 0, 2, 2],
        ReplacementGroup.add_all([(0, 3, ['a']), (5, 6, ['a', 'b', 'c']),
                                  (7, 9, ['a', 'b', 'c', 'd'])]),
        [1, 0, 0, 3, 3, 3, 0, 2, 2, 2, 2],
        ReplacementGroup.add_all([(0, 1, ['a', 'b', 'c']), (3, 6, ['a']),
                                  (7, 11, ['a', 'b'])]),
        id='list-modify',
    ),
    pytest.param(
        [1, 2, 3, 4],
        ReplacementGroup.add_all([(0, 0, 'a'), (1, 1, 'abc'), (4, 4, 'abcd')]),
        [0, 1, 0, 0, 0, 2, 3, 4, 0, 0, 0, 0],
        ReplacementGroup.add_all([(0, 1, ''), (2, 5, ''), (8, 12, '')]),
        id='str-insert',
    ),
    pytest.param(
        [1, 2, 3, 4],
        ReplacementGroup.add_all([(0, 0, ['a']), (1, 1, ['a', 'b', 'c']),
                                  (4, 4, ['a', 'b', 'c', 'd'])]),
        [0, 1, 0, 0, 0, 2, 3, 4, 0, 0, 0, 0],
        ReplacementGroup.add_all([(0, 1, []), (2, 5, []), (8, 12, [])]),
        id='list-insert',
    ),
]

not_invertible_test_cases = [
    pytest.param(
        [1, 2, 3, 4, 5, 6],
        ReplacementGroup.add_all([(0, 1, ''), (2, 4, ''), (5, 6, '')]),
        [2, 5],
        ReplacementGroup.add_all([(0, 0, 'a'), (1, 1, 'ab'), (2, 2, 'c')]),
        id='str-delete',
    ),
    pytest.param(
        [1, 2, 3, 4, 5, 6],
        ReplacementGroup.add_all([(0, 1, []), (2, 4, []), (5, 6, [])]),
        [2, 5],
        ReplacementGroup.add_all([(0, 0, ['a']), (1, 1, ['a', 'b']), (2, 2, ['c'])]),
        id='list-delete',
    ),
]


@pytest.mark.parametrize(
    "input_label,forward_replacements,output_label,inverse_replacements",
    test_cases + not_invertible_test_cases,
)
def test_forward_propagate_by_replacement_group(
        input_label, forward_replacements, output_label, inverse_replacements):
    output = propagate_by_replacement_group(input_label, forward_replacements)
    assert output_label == output


@pytest.mark.parametrize(
    "input_label,forward_replacements,output_label,inverse_replacements",
    test_cases,
)
def test_backward_propagate_by_replacement_group(
        input_label, forward_replacements, output_label, inverse_replacements):
    output = propagate_by_replacement_group(output_label, inverse_replacements)
    assert input_label == output


@pytest.mark.parametrize(
    "input_label,forward_replacements,output_label,inverse_replacements",
    not_invertible_test_cases,
)
def test_not_invertible(input_label, forward_replacements, output_label, inverse_replacements):
    output = propagate_by_replacement_group(output_label, inverse_replacements)
    assert [0, 2, 0, 0, 5, 0] == output


def test_propagate_by_span_group():
    span_group = SpanGroup.add_all([(0, 2), (2, 5)])
    output_label = reduce_by_span_group([2, 2, 3, 5, 5], span_group)
    assert [2, 5] == output_label
    reverse_label = expand_by_span_group(output_label, span_group)
    assert reverse_label == [2, 2, 5, 5, 5]


@pytest.mark.parametrize(
    "labels,func,spans",
    [
        pytest.param(
            [1, 2, 3, 4, 5],
            reduce_by_span_group,
            SpanGroup.add_all([(0, 2), (2, 4)]),
            id='max length',
        ),
        pytest.param(
            [1, 2, 3],
            expand_by_span_group,
            SpanGroup.add_all([(0, 2), (2, 4)]),
            id='number',
        ),
    ],
)
def test_span_group_not_competible(labels, func, spans):
    with pytest.raises(ValueError):
        func(labels, spans)


@pytest.mark.parametrize(
    "by,group",
    [
        pytest.param(
            propagate_by_replacement_group,
            ReplacementGroup.add_all([(0, 2, 'a'), (2, 5, 'b')]),
            id='replacement-group',
        ),
        pytest.param(
            reduce_by_span_group,
            SpanGroup.add_all([(0, 2), (2, 5)]),
            id='span-group',
        ),
    ],
)
def test_different_transduce_func(by, group):
    def zero_transduce(x, output_size):
        return [0] * output_size
    assert [0, 0] == by([1, 2, 3, 4, 5], group, zero_transduce)


def test_intersection_case_of_span_propagation():
    labels = [1]
    span_group = SpanGroup.add_all([(0, 1)])
    assert labels == reduce_by_span_group(labels, span_group)
    assert labels == expand_by_span_group(labels, span_group)

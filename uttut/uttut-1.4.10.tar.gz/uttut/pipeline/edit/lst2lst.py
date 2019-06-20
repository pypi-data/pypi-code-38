from .replacement import ReplacementGroup
from .utils import (
    _transform_sequence,
    _gen_inverse_replacement_group,
)


def apply(input_lst: list, replacement_group: ReplacementGroup) -> list:
    output: list
    n_replacement = len(replacement_group)
    output = [[]] * (2 * n_replacement + 1)
    output_lst = _transform_sequence(
        input_seq=input_lst,
        replacement_group=replacement_group,
        output=output,
    )
    return sum(output_lst, [])


def inverse(input_lst: list, replacement_group: ReplacementGroup) -> ReplacementGroup:
    inverse_replacement_group = _gen_inverse_replacement_group(
        input_seq=input_lst,
        replacement_group=replacement_group,
    )
    assert len(inverse_replacement_group) == len(replacement_group)
    return inverse_replacement_group

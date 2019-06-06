from typing import List, Tuple

from .base import Operator, LabelAligner
from .label_transducer import get_most_common_except_not_entity
from ..edit.replacement import ReplacementGroup
from ..edit import str2str
from ..edit.label_propagation import propagate_by_replacement_group
from uttut import ENTITY_LABEL


class AddWhitespaceAroundCharacter(Operator):

    """
    Base class for Operators which recognize the characters using function `_is_valid_char`
    and add whitespace around the matched one
    """

    _input_type = str
    _output_type = str

    def _transform(self, input_sequence: str) -> Tuple[str, 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = str2str.apply(input_sequence, forward_replacement_group)

        label_aligner = AddWhitespaceAroundCharAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_str: str) -> ReplacementGroup:
        replacement_group = ReplacementGroup()

        for i, char in enumerate(input_str):
            if self._is_valid_char(char):
                replacement_group.add(
                    start=i,
                    end=i + 1,
                    new_value=f" {char} ",
                    annotation="add-whitespace-around-any-CJK-char",
                )

        replacement_group.done()
        return replacement_group

    def _is_valid_char(self, char: str) -> bool:
        raise NotImplementedError


class AddWhitespaceAroundCharAligner(LabelAligner):

    def _transform(self, labels: List[int]) -> ReplacementGroup:
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._forward_edit,
            transduce_func=self._forward_transduce_func,
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        assert len(labels) == 1
        return [ENTITY_LABEL['NOT_ENTITY'], labels[0], ENTITY_LABEL['NOT_ENTITY']]

    def _inverse_transform(self, labels):
        inverse_replacement_group = str2str.inverse(self._input_sequence, self._forward_edit)
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=inverse_replacement_group,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)

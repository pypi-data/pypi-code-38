from typing import List, Tuple

from .base import Operator, LabelAligner
from ..edit.replacement import ReplacementGroup
from ..edit import str2str
from ..edit.label_propagation import propagate_by_replacement_group
from .add_whitespace_around_punctuation import is_punctuation
from .label_transducer import get_not_entity


class PunctuationExceptEndpointToWhitespace(Operator):

    """
    Recognize punctuation characters except endpoint (`.`) and
    replace it with whitespace (" ")

    E.g.
    >>> from uttut.pipeline.ops.punctuation_except_endpoint_to_whitespace import (
        PunctuationExceptEndpointToWhitespace)
    >>> op = PunctuationExceptEndpointToWhitespace()
    >>> output_seq, label_aligner = op.transform("GB,薄餡亂入")
    >>> output_labels = label_aligner.transform([1, 1, 2, 3, 3, 4, 5])
    >>> output_seq
    "GB 薄餡亂入"
    >>> output_labels
    [1, 1, 0, 2, 3, 3, 4, 5]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 1, 0, 2, 3, 3, 4, 5]

    """

    _input_type = str
    _output_type = str

    def _transform(self, input_sequence: str) -> Tuple[str, 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = str2str.apply(input_sequence, forward_replacement_group)

        label_aligner = PunctuationExceptEndpointToWhitespaceAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_str: str) -> ReplacementGroup:
        replacement_group = ReplacementGroup()

        for i, char in enumerate(input_str):
            if is_punctuation(char) and not self._is_endpoint(char):
                replacement_group.add(
                    start=i,
                    end=i + 1,
                    new_value=" ",
                    annotation="replace-punctuations-with-whitespace-except-endpoint",
                )
        replacement_group.done()
        return replacement_group

    def _is_endpoint(self, char: str) -> bool:
        if char == ".":
            return True
        return False


class PunctuationExceptEndpointToWhitespaceAligner(LabelAligner):

    def _transform(self, labels: List[int]):
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._forward_edit,
            transduce_func=self._forward_transduce_func,
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels, output_size)

    def _inverse_transform(self, labels):
        inverse_replacement_group = str2str.inverse(self._input_sequence, self._forward_edit)
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=inverse_replacement_group,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels, output_size)

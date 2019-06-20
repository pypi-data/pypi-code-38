from typing import List, Tuple
import unicodedata

from .base import Operator, LabelAligner
from .label_transducer import get_most_common_except_not_entity
from ..edit.replacement import ReplacementGroup
from ..edit import str2str
from ..edit.label_propagation import propagate_by_replacement_group


class StripAccentToken(Operator):

    """
    Strip accent token

    E.g.
    >>> from uttut.pipeline.ops.strip_accent_token import StripAccentToken
    >>> op = StripAccentToken()
    >>> output_seq, label_aligner = op.transform(u"H\u00E9llo")
    >>> output_labels = label_aligner.transform([1, 2, 3, 4, 5])
    >>> output_seq
    "Hello"
    >>> output_labels
    [1, 2, 3, 4, 5]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3, 4, 5]

    """

    _input_type = str
    _output_type = str

    def _transform(self, input_sequence: str) -> Tuple[str, 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = str2str.apply(input_sequence, forward_replacement_group)

        label_aligner = StripAccentTokenAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_str: str) -> ReplacementGroup:
        replacement_group = ReplacementGroup()
        output_str = _strip_accents(input_str)
        assert len(input_str) == len(output_str)

        for i, (input_char, output_char) in enumerate(zip(input_str, output_str)):
            if input_char != output_char:
                replacement_group.add(
                    start=i,
                    end=i + 1,
                    new_value=output_char,
                    annotation="strip-accent-token",
                )
        replacement_group.done()
        return replacement_group


class StripAccentTokenAligner(LabelAligner):

    def _transform(self, labels: List[int]) -> List[int]:
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._forward_edit,
            transduce_func=self._forward_transduce_func,
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)

    def _inverse_transform(self, labels: List[int]) -> List[int]:
        inverse_replacement_group = str2str.inverse(self._input_sequence, self._forward_edit)
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=inverse_replacement_group,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


def _strip_accents(text: str) -> str:

    """Strips accents from a piece of text

    This code is copied from Bert `tokenization.py`.

    """

    text = unicodedata.normalize("NFD", text)
    output = []
    for char in text:
        cat = unicodedata.category(char)
        if cat == "Mn":
            continue
        output.append(char)
    return "".join(output)

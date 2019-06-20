from typing import Tuple

import re

from .base import Operator, NullLabelAligner
from ..edit.replacement import ReplacementGroup
from ..edit import str2str


class Lowercase(Operator):

    """
    Recognize uppercase characters and convert them into lowercase characters

    E.g.
    >>> from uttut.pipeline.ops.lowercase import Lowercase
    >>> op = Lowercase()
    >>> output_seq, label_aligner = op.transform("ABc")
    >>> output_labels = label_aligner.transform([1, 2, 3])
    >>> output_seq
    "abc"
    >>> output_labels
    [1, 2, 3]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3]

    """

    _input_type = str
    _output_type = str

    REGEX_PATTERN = re.compile(r"[A-Z]+")

    def _transform(self, input_sequence: str) -> Tuple[str, 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = str2str.apply(input_sequence, forward_replacement_group)
        assert len(input_sequence) == len(output_sequence)

        label_aligner = LowercaseAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_str: str) -> ReplacementGroup:
        shift = 0
        replacement_group = ReplacementGroup()

        while shift < len(input_str):
            match = self.REGEX_PATTERN.search(input_str, shift)
            if match is None:
                break
            matched_str = input_str[match.start(): match.end()]
            replacement_group.add(
                start=match.start(),
                end=match.end(),
                new_value=matched_str.lower(),
                annotation='lowercase',
            )
            shift = match.end()
        replacement_group.done()
        return replacement_group


LowercaseAligner = NullLabelAligner

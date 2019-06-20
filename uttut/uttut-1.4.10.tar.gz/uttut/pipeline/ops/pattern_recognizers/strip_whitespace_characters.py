from typing import List

import re

from ..label_transducer import get_not_entity
from .base import PatternRecognizer, PatternRecognizerAligner


class StripWhiteSpaceCharactersAligner(PatternRecognizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)


class StripWhiteSpaceCharacters(PatternRecognizer):

    """
    Recognize leading and trailing whitespace characters in the string
    and replace them with an empty string ("")

    E.g.
    >>> from uttut.pipeline.ops.strip_whitespace_characters import StripWhiteSpaceCharacters
    >>> op = StripWhiteSpaceCharacters()
    >>> output_seq, label_aligner = op.transform(" a\n")
    >>> output_labels = label_aligner.transform([1, 2, 3])
    >>> output_seq
    "a"
    >>> output_labels
    [2]
    >>> label_aligner.inverse_transform(output_labels)
    [0, 2, 0]

    """

    _label_aligner_class = StripWhiteSpaceCharactersAligner

    REGEX_PATTERN = re.compile(r"\A\s+|\s+\Z")
    TOKEN = ""

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='strip whitespace',
        )

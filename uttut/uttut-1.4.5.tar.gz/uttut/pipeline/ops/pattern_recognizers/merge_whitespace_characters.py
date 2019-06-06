from typing import List

import re

from ..label_transducer import get_most_common
from .base import PatternRecognizer, PatternRecognizerAligner


class MergeWhiteSpaceCharactersAligner(PatternRecognizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common(labels=labels, output_size=output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common(labels=labels, output_size=output_size)


class MergeWhiteSpaceCharacters(PatternRecognizer):

    """
    Recognize contiguous whitespace characters in the string
    and replace it with a whitespace character (" ")

    E.g.
    >>> from uttut.pipeline.ops.merge_whitespace_characters import MergeWhiteSpaceCharacters
    >>> op = MergeWhiteSpaceCharacters()
    >>> output_seq, label_aligner = op.transform("\n\n  \t\t")
    >>> output_labels = label_aligner.transform([1, 1, 1, 1, 1, 1])
    >>> output_seq
    " "
    >>> output_labels
    [0]
    >>> label_aligner(output_labels)
    [0, 0, 0, 0, 0, 0]

    """

    _label_aligner_class = MergeWhiteSpaceCharactersAligner

    REGEX_PATTERN = re.compile(r"\s+")
    TOKEN = " "

from typing import List

import re

from ..label_transducer import get_most_common, get_most_common_except_not_entity
from ..tokens import INT_TOKEN
from .base import PatternRecognizer, PatternRecognizerAligner


class IntTokenAligner(PatternRecognizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common(labels=labels, output_size=output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


class IntToken(PatternRecognizer):
    """
    Recognize integer (ex: 12, 10000) in the input string
    and replace them with INT_TOKEN (_int_)

    E.g.
    >>> from uttut.pipeline.ops.int_token import IntToken
    >>> op = IntToken()
    >>> output_seq, realigner = op.transform("10")
    >>> output_labels = label_aligner.transform([1, 1])
    >>> output_seq
    "_int_"
    >>> output_labels
    [1, 1, 1, 1, 1]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 1]

    """

    _label_aligner_class = IntTokenAligner

    REGEX_PATTERN = re.compile(r"(?<![\.\d\uFF10-\uFF19])[\d\uFF10-\uFF19]+(?![\.\d\uFF10-\uFF19])")
    TOKEN = INT_TOKEN

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='int-token',
        )

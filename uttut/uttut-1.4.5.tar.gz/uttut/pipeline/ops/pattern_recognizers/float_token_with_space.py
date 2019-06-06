from typing import List
import re
from collections import Counter

from uttut import ENTITY_LABEL
from ..label_transducer import get_most_common_except_not_entity
from ..tokens import FLOAT_TOKEN_WITH_SPACE
from .base import PatternRecognizer, PatternRecognizerAligner


class FloatTokenWithSpaceAligner(PatternRecognizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        token = FloatTokenWithSpace.TOKEN
        counter = Counter(labels)
        common_label = counter.most_common()[0][0]
        token_len = len(token) - 2
        output_label = [ENTITY_LABEL['NOT_ENTITY']] + \
            [common_label] * token_len + [ENTITY_LABEL['NOT_ENTITY']]
        return output_label

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


class FloatTokenWithSpace(PatternRecognizer):
    """
    Recognize integer (ex: 12.3, 100.77) in the input string
    and replace them with FLOAT_TOKEN_WTIH_SPACE ( _float_ )

    Note that extra spaces are added behind and after the FLOAT_TOKEN.

    E.g.
    >>> from uttut.pipeline.ops.float_token_with_space import FloatTokenWithSpace
    >>> op = FloatTokenWithSpace()
    >>> output_seq, label_aligner = op.transform("10.7")
    >>> output_labels = label_aligner.transform([1, 1, 1, 1])
    >>> output_seq
    " _float_ "
    >>> output_labels
    [0, 1, 1, 1, 1, 1, 1, 1, 0]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 1, 1, 1]

    """

    _label_aligner_class = FloatTokenWithSpaceAligner

    REGEX_PATTERN = re.compile(r"(?<![\.\d])\d+\.\d+(?![\.\d])")
    TOKEN = FLOAT_TOKEN_WITH_SPACE

    def _gen_forward_replacement_group(self, input_str: str):  # type: ignore
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='float-token-with-space',
        )

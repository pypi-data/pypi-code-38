from typing import List
import re
from ..label_transducer import get_most_common_except_not_entity
from .base import PatternRecognizer, PatternRecognizerAligner


class ReplaceAwithBAligner(PatternRecognizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


class ReplaceAwithB(PatternRecognizer):

    """
    Recognize a (pattern or substring)  in the input string
    and replace them with b.

    E.g.
    >>> from uttut.pipeline.ops.pattern_recognizers.replace_a_with_b import
    ReplaceAwithB
    >>> op = ReplaceAwithB(a=r'[\.]+', b="X")
    >>> output_seq, label_aligner = op.transform("10....7")
    >>> output_labels = label_aligner.transform([1, 1, 1, 2, 1, 1, 1])
    >>> output_seq
    "10X7"
    >>> output_labels
    [1, 1, 1, 1]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 1, 1, 1, 1, 1, 1]

    """  # noqa: W605

    _label_aligner_class = ReplaceAwithBAligner

    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.REGEX_PATTERN = re.compile(self.a)
        self.TOKEN = self.b

    def _gen_forward_replacement_group(self, input_str: str):
        return super()._gen_forward_replacement_group(
            input_str=input_str,
            annotation='replace-a-with-b',
        )

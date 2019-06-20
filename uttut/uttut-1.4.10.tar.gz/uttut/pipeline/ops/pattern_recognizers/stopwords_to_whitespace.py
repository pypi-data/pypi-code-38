from typing import List
import os
import re

from ..label_transducer import get_not_entity
from .base import PatternRecognizer, PatternRecognizerAligner


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class StopwordsToWhitespaceAligner(PatternRecognizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_not_entity(labels=labels, output_size=output_size)


class StopwordsToWhitespace(PatternRecognizer):

    """
    Recognize stopwords and replace it with a whitespace character (" ")

    E.g.
    >>> from uttut.pipeline.ops.pattern_recognizer.stopwords_to_whitespace
    import StopwordsToWhitespace
    >>> op = StopwordsToWhitespace()
    >>> output_seq, label_aligner = op.transform("哎呀,你好嗎"")
    >>> output_labels = label_aligner.transform([1, 2, 3, 4, 5, 6])
    >>> output_seq
    " ,你好 "
    >>> output_labels
    [0, 3, 4, 5, 0]
    >>> label_aligner(output_labels)
    [0, 0, 3, 4, 5, 0]

    """

    _label_aligner_class = StopwordsToWhitespaceAligner

    with open(os.path.join(ROOT_DIR, 'stopwords.txt'), 'r') as reader:
        stopwords_str = reader.read()
    stopwords_str = stopwords_str.replace("\n", "|")

    REGEX_PATTERN = re.compile(r"(" + stopwords_str + ")")
    TOKEN = " "

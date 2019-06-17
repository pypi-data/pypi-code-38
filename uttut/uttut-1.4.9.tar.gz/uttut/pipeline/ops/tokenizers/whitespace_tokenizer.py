from typing import List

from ..label_transducer import get_most_common_except_not_entity
from .base import Tokenizer, TokenizerAligner


class WhiteSpaceTokenizerAligner(TokenizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


class WhiteSpaceTokenizer(Tokenizer):

    """
    Spilt input string into pieces by whitespace characters

    This is a modification of `whitespace_tokenize` in Bert `tokenization.py`.

    E.g.
    >>> from uttut.pipeline.ops.whitespace_tokenizer import WhiteSpaceTokenizer
    >>> op = WhiteSpaceTokenizer()
    >>> output_seq, label_aligner = op.transform("a b")
    >>> output_labels = label_aligner.transform([1, 2, 3])
    >>> output_seq
    ["a", "b"]
    >>> output_labels
    [1, 3]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 0, 3]

    """

    _label_aligner_class = WhiteSpaceTokenizerAligner

    def _tokenize(self, input_str: str) -> List[str]:
        """Split text into list by whitespace characters

        E.g.
        1. "a  \t\t\n\n b" -> ["a", "b"]
        2. "  \n\t\n  " -> []
        3. "  a b \t\n" -> ["a", "b"]

        """
        return input_str.split()

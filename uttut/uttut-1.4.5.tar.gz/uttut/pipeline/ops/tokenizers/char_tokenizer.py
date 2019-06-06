from typing import List

from .base import Tokenizer, TokenizerAligner


class CharTokenizerAligner(TokenizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        pass

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        pass


class CharTokenizer(Tokenizer):

    """Character level tokenizer

    E.g.
    >>> from uttut.pipeline.ops.char_tokenizer import CharTokenizer
    >>> op = CharTokenizer()
    >>> output_seq, label_aligner = op.transform("a b")
    >>> output_labels = label_aligner.transform([1, 2, 3])
    >>> output_seq
    ["a", "b"]
    >>> output_labels
    [1, 3]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 0, 3]

    """

    _label_aligner_class = CharTokenizerAligner

    def _tokenize(self, input_str: str) -> List[str]:
        return list(input_str)

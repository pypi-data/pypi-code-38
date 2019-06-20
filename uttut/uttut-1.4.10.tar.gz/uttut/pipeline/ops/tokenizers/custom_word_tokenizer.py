from typing import List

from ..label_transducer import get_most_common_except_not_entity
from ..utils.trie import Trie
from .base import Tokenizer, TokenizerAligner


class CustomWordTokenizerAligner(TokenizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


class CustomWordTokenizer(Tokenizer):

    """Word Tokenizer Given User Words

    E.g.
    >>> from uttut.pipeline.ops.custom_word_tokenizer import CustomWordTokenizer
    >>> op = CustomWordTokenizer(['珍奶', '珍奶去冰', '去冰'])
    >>> output_seq, label_aligner = op.transform("一杯珍奶去冰")
    >>> output_labels = label_aligner.transform([1, 2, 3, 3, 3, 0])
    >>> output_seq
    ["一", "杯", "珍奶去冰"]
    >>> output_labels
    [1, 2, 3]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3, 3, 3, 3]

    """

    _label_aligner_class = CustomWordTokenizerAligner

    def __init__(self, user_words: List[str], shortest: bool = False):
        self.validate_user_words(user_words)
        self._user_words = user_words
        self._trie = Trie()
        for word in self._user_words:
            self._trie.insert(word)

        self._shortest = shortest

    @staticmethod
    def validate_user_words(user_words):
        if user_words is None or len(user_words) < 1:
            raise ValueError('User words should not be empty.')

    def _tokenize(self, input_str: str) -> List[str]:
        start = 0
        tokens = []
        while start < len(input_str):
            match_result = self._trie.match_prefix(
                input_str[start:],
                shortest=self._shortest,
            )
            if match_result is None:
                token = input_str[start: start + 1]
                start += 1
            else:
                token = match_result
                start += len(match_result)
            tokens.append(token)
        return tokens

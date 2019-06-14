from typing import List

import unicodedata

from ..label_transducer import get_most_common_except_not_entity
from .base import Tokenizer, TokenizerAligner


class EngTokenizerAligner(TokenizerAligner):

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return get_most_common_except_not_entity(labels, output_size)


class EngTokenizer(Tokenizer):

    """English Word level tokenizer

    All of following functions are copied from BERT.
    https://github.com/google-research/bert/blob/master/tokenization.py

    E.g.
    >>> from uttut.pipeline.ops.eng_tokenizer import EngTokenizer
    >>> op = EngTokenizer()
    >>> output_seq, label_aligner = op.transform("a b")
    >>> output_labels = label_aligner.transform([1, 2, 3])
    >>> output_seq
    ["a", "b"]
    >>> output_labels
    [1, 3]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 0, 3]

    """

    _label_aligner_class = EngTokenizerAligner

    def _tokenize(self, input_str: str) -> List[str]:
        orig_tokens = whitespace_tokenize(input_str)
        split_tokens = []
        for token in orig_tokens:
            split_tokens.extend(self._run_split_on_punc(token))
        output_tokens = whitespace_tokenize(" ".join(split_tokens))
        return output_tokens

    def _run_split_on_punc(self, text: str) -> List[str]:
        """
        Recognize punctuations and seperate them into independent tokens.

        E.g.
        1. "abc, cdf" -> ["abc", ",", " ", "cdf"]
        2. "I like apples." -> ["I", "like", "apples", "."]

        """
        chars = list(text)
        i = 0
        start_new_word = True
        output = []
        while i < len(chars):
            char = chars[i]
            if _is_punctuation(char):
                output.append([char])
                start_new_word = True
            else:
                if start_new_word:
                    output.append([])
                start_new_word = False
                output[-1].append(char)
            i += 1
        return ["".join(x) for x in output]


def whitespace_tokenize(text: str) -> List[str]:
    """Split text into list by whitespace characters

    E.g.
    1. "a  \t\t\n\n b" -> ["a", "b"]
    2. "  \n\t\n  " -> []
    3. "  a b \t\n" -> ["a", "b"]

    """
    tokens = text.split()
    return tokens


def _is_punctuation(char):
    """Checks whether `chars` is a punctuation character.

    We treat all non-letter/number ASCII as punctuation.
    Characters such as "^", "$", and "`" are not in the Unicode
    Punctuation class but we treat them as punctuation anyways, for
    consistency.

    """
    cp = ord(char)
    if (
        (cp >= 33 and cp <= 47) or (
            cp >= 58 and cp <= 64) or (
            cp >= 91 and cp <= 96) or (
            cp >= 123 and cp <= 126)
    ):
        return True
    cat = unicodedata.category(char)
    if cat.startswith("P"):
        return True
    return False

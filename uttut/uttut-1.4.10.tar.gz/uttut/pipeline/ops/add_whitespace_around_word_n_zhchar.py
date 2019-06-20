from typing import List, Tuple

from .base import Operator, LabelAligner
from ..edit.replacement import ReplacementGroup
from ..edit import str2str
from ..edit.label_propagation import propagate_by_replacement_group
from uttut import ENTITY_LABEL

from .utils.trie import Trie


class AddWhitespaceAroundWordnZhChar(Operator):

    """
    Given list of words, add whitespace around indicated words and CJK characters.
    Ignore characters which are not CJK.

    E.g.
    >>> from uttut.pipeline.ops.add_whitespace_around_word_n_zhchar import
    AddWhitespaceAroundWordnZhChar
    >>> op = AddWhitespaceAroundWordnZhChar(user_words=['珍奶', '珍奶去冰', '去冰'])
    >>> output_seq, label_aligner = op.transform("GB要一杯珍奶去冰")
    >>> output_labels = label_aligner.transform([1, 2, 3, 4, 5, 6, 7, 8, 9])
    >>> output_seq
    "GB 要  一  杯  珍奶去冰 "
    >>> output_labels
    [1, 2, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 7, 8, 9, 0]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> op = AddWhitespaceAroundWordnZhChar(user_words=['珍奶', '珍奶去冰', '去冰'], shortest=True)
    >>> output_seq, label_aligner = op.transform("GB要一杯珍奶去冰")
    >>> output_labels = label_aligner.transform([1, 2, 3, 4, 5, 6, 7, 8, 9])
    >>> output_seq
    "GB 要  一  杯  珍奶  去冰 "
    >>> output_labels
    [1, 2, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 7, 0, 0, 8, 9, 0]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

    """

    _input_type = str
    _output_type = str

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

    def _transform(self, input_sequence: str) -> Tuple[str, 'LabelAligner']:
        forward_replacement_group = self._gen_forward_replacement_group(input_sequence)
        output_sequence = str2str.apply(input_sequence, forward_replacement_group)

        label_aligner = AddWhitespaceAroundWordAligner(
            input_sequence=input_sequence,
            edit=forward_replacement_group,
            output_length=len(output_sequence),
        )
        return output_sequence, label_aligner

    def _gen_forward_replacement_group(self, input_str: str) -> ReplacementGroup:
        start = 0
        replacement_group = ReplacementGroup()
        while start < len(input_str):
            match_result = self._trie.match_prefix(
                input_str[start:],
                shortest=self._shortest,
            )
            if match_result is not None:
                # word level
                token = match_result
                replacement_group.add(
                    start=start,
                    end=start + len(token),
                    new_value=f" {token} ",
                    annotation="add-whitespace-around-word",
                )
                start += len(token)
            else:
                # char level
                char = input_str[start: start + 1]
                if self._is_valid_char(char):
                    replacement_group.add(
                        start=start,
                        end=start + 1,
                        new_value=f" {char} ",
                        annotation="add-whitespace-around-word",
                    )
                start += 1
        replacement_group.done()
        return replacement_group

    def _is_valid_char(self, char: str) -> bool:
        """Check whether input char is the codepoint of a CJK character.

        This code is copied from Bert `tokenization.py`.

        This defines a "chinese character" as anything in the CJK Unicode block:
        https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)

        Note that the CJK Unicode block is NOT all Japanese and Korean characters,
        despite its name. The modern Korean Hangul alphabet is a different block,
        as is Japanese Hiragana and Katakana. Those alphabets are used to write
        space - separated words, so they are not treated specially and handled
        like the all of the other languages.

        """
        code_point = ord(char)
        if ((
                code_point >= 0x4E00 and code_point <= 0x9FFF) or (
                code_point >= 0x3400 and code_point <= 0x4DBF) or (
                code_point >= 0x20000 and code_point <= 0x2A6DF) or (
                code_point >= 0x2A700 and code_point <= 0x2B73F) or (
                code_point >= 0x2B740 and code_point <= 0x2B81F) or (
                code_point >= 0x2B820 and code_point <= 0x2CEAF) or (
                code_point >= 0xF900 and code_point <= 0xFAFF) or (
                code_point >= 0x2F800 and code_point <= 0x2FA1F)
            ):
            return True

        return False


class AddWhitespaceAroundWordAligner(LabelAligner):

    def _transform(self, labels: List[int]) -> ReplacementGroup:
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=self._forward_edit,
            transduce_func=self._forward_transduce_func,
        )

    def _forward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        output_labels = [ENTITY_LABEL['NOT_ENTITY']]
        output_labels.extend(labels)
        output_labels.append(ENTITY_LABEL['NOT_ENTITY'])
        return output_labels

    def _inverse_transform(self, labels):
        inverse_replacement_group = str2str.inverse(self._input_sequence, self._forward_edit)
        return propagate_by_replacement_group(
            labels=labels,
            replacement_group=inverse_replacement_group,
            transduce_func=self._backward_transduce_func,
        )

    def _backward_transduce_func(self, labels: List[int], output_size: int) -> List[int]:
        return labels[1: -1]

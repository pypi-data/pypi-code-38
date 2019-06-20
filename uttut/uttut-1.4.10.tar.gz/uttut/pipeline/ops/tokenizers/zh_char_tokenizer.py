from typing import List

from .eng_tokenizer import EngTokenizer


class ZhCharTokenizer(EngTokenizer):

    """Chinese Character level tokenizer

    All of following functions are copied from BERT.
    https://github.com/google-research/bert/blob/master/tokenization.py

    E.g.
    >>> from uttut.pipeline.ops.zh_char_tokenizer import ZhCharTokenizer
    >>> op = ZhCharTokenizer()
    >>> output_seq, label_aligner = op.transform("這是a b")
    >>> output_labels = label_aligner.transform([1, 2, 3, 4, 5])
    >>> output_seq
    ["這", "是", "a", "b"]
    >>> output_labels
    [1, 2, 3, 5]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 2, 3, 0, 5]

    """

    def _tokenize(self, input_str: str) -> List[str]:
        text = self._tokenize_chinese_chars(input_str)
        return super()._tokenize(text)

    def _tokenize_chinese_chars(self, text):
        """Recognize CJK character and add whitespace around it

        E.g.
        1. "我喜歡吃蘋果" -> " 我  喜  歡  吃  蘋  果 "
        2. "我喜歡吃apples." -> " 我  喜  歡  吃 apples."

        """
        output = []
        for char in text:
            code_position = ord(char)
            if self._is_chinese_char(code_position):
                output.append(" ")
                output.append(char)
                output.append(" ")
            else:
                output.append(char)
        return "".join(output)

    def _is_chinese_char(self, code_position):
        """Checks whether CP is the codepoint of a CJK character.

        This defines a "chinese character" as anything in the CJK Unicode block:
        https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)

        Note that the CJK Unicode block is NOT all Japanese and Korean characters,
        despite its name. The modern Korean Hangul alphabet is a different block,
        as is Japanese Hiragana and Katakana. Those alphabets are used to write
        space-separated words, so they are not treated specially and handled
        like the all of the other languages.

        """
        if ((code_position >= 0x4E00 and code_position <= 0x9FFF) or (
                code_position >= 0x3400 and code_position <= 0x4DBF) or (
                code_position >= 0x20000 and code_position <= 0x2A6DF) or (
                code_position >= 0x2A700 and code_position <= 0x2B73F) or (
                code_position >= 0x2B740 and code_position <= 0x2B81F) or (
                code_position >= 0x2B820 and code_position <= 0x2CEAF) or(
                code_position >= 0xF900 and code_position <= 0xFAFF) or (
                code_position >= 0x2F800 and code_position <= 0x2FA1F)):  #
            return True
        return False

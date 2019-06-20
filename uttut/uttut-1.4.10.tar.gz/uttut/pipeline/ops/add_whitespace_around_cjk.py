from .add_whitespace_around_character import AddWhitespaceAroundCharacter


class AddWhitespaceAroundCJK(AddWhitespaceAroundCharacter):

    """
    Recognize CJK characters and add whitespace around each CJK character

    E.g.
    >>> from uttut.pipeline.ops.add_whitespace_around_cjk import AddWhitespaceAroundCJK
    >>> op = AddWhitespaceAroundCJK()
    >>> output_seq, label_aligner = op.transform("GB亂入")
    >>> output_labels = label_aligner.transform([1, 1, 2, 3])
    >>> output_seq
    "GB 亂  入 "
    >>> output_labels
    [1, 1, 0, 2, 0, 0, 3, 0]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 1, 2, 3]

    """

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

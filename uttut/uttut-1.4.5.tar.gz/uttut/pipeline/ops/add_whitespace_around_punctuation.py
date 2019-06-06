import unicodedata

from .add_whitespace_around_character import AddWhitespaceAroundCharacter


class AddWhitespaceAroundPunctuation(AddWhitespaceAroundCharacter):

    """
    Recognize punctuation characters and add whitespace around each punctuation character

    E.g.
    >>> from uttut.pipeline.ops.add_whitespace_around_punctuation import (
        AddWhitespaceAroundPunctuation)
    >>> op = AddWhitespaceAroundPunctuation()
    >>> output_seq, label_aligner = op.transform("GB,薄餡亂入")
    >>> output_labels = label_aligner.transform([1, 1, 2, 3, 3, 4, 5])
    >>> output_seq
    "GB , 薄餡亂入"
    >>> output_labels
    [1, 1, 0, 2, 0, 3, 3, 4, 5]
    >>> label_aligner.inverse_transform(output_labels)
    [1, 1, 2, 3, 3, 4, 5]

    """

    def _is_valid_char(self, char: str) -> bool:
        return is_punctuation(char)


def is_punctuation(char: str) -> bool:
    """Check whether char is a punctuation character.

    This code is copied from Bert `tokenization.py`.

    We treat all non-letter/number ASCII as punctuation.
    Characters such as "^", "$", and "`" are not in the Unicode
    Punctuation class but we treat them as punctuation anyways, for
    consistency.

    """
    code_point = ord(char)
    if ((
            code_point >= 33 and code_point <= 47) or (
            code_point >= 58 and code_point <= 64) or (
            code_point >= 91 and code_point <= 96) or (
            code_point >= 123 and code_point <= 126)
        ):
        return True

    cat = unicodedata.category(char)
    # For more details, please take a look at
    # https://www.fileformat.info/info/unicode/category/index.htm
    if cat.startswith("P"):
        return True

    return False

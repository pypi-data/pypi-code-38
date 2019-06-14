"""
A file that contains utilities to detect if a hashtag refers to a disaster, as well as disaster hashtag-generating
utilities.
"""
import re
from typing import Union


def contains_hashtag(text, hashtag):
    # type: (str, str) -> bool
    """Tells you if text contains a hashtag.

    :param text: Text to search in.
    :param hashtag: Hashtag to search for.
    :return: If the hashtag exists in the text.
    """

    return ensure_hashtag(hashtag) in extract_hashtags(text)


REGEX_ALPHABETIC_HASHTAG = "#\\w+"


def ensure_hashtag(text):
    # type: (str) -> str
    """Ensure that `text` begins with '#'."""

    if len(text) is 0:  # Empty string
        return '#' + text

    if text[0] == '#':  # Starts with '#'
        return text

    return '#' + text  #


def extract_hashtags(text):
    # type: (Union[str, unicode]) -> set[str]
    """Given text, will return all hashtags present in the text.
    This assumes hashtags are alphabetic.

    TODO test non-western chars like مرحبا, 你好, or नमस्ते.
    """
    matches = re.findall(REGEX_ALPHABETIC_HASHTAG, text)
    return set(matches)

import re

NORMALIZE_WHITESPACE_REGEX = re.compile(r'(\s|\\xa0)+')


def normalize_whitespace(text):
    """
    Normalize the whitespace in the provided text so that
    all space characters (spaces, newlines, tags, ...) is
    replaced by a single space.

    Args:
        text (str): The string to normalize.

    Returns:
        str: The normalized text.
    """
    return NORMALIZE_WHITESPACE_REGEX.sub(' ', text)

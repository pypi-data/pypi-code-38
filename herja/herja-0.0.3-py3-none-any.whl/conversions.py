"""A collection of common object conversions."""


from bs4 import BeautifulSoup

from .assertions import assert_type
from .constants import UTF_8, MINUTE, HOUR


def html_to_soup(html):
    """Convert given html to a soup object."""
    return BeautifulSoup(html, 'html.parser')


def ms_to_hours(milliseconds):
    """Convert milliseconds to hours."""
    return seconds_to_hours(milliseconds / 1000)


def seconds_to_hours(seconds):
    """Convert seconds to hours."""
    return seconds / HOUR


def seconds_to_minutes(seconds):
    """Convert seconds to minutes."""
    return seconds / MINUTE


def to_bytes(convert, encoding=UTF_8):
    """Convert a given string to bytes."""
    if isinstance(convert, str):
        return convert.encode(encoding)
    assert_type(convert, bytes)
    return convert


def to_str(convert, decoding=UTF_8):
    """Convert a given set of bytes to a string."""
    if isinstance(convert, bytes):
        return convert.decode(decoding)
    assert_type(convert, str)
    return convert

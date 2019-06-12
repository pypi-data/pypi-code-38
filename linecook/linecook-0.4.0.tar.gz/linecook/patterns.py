# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def any_of(*args):
    """Return regex that matches any of the input regex patterns.

    The returned value is equivalent to writing::

        r'(<arg1>|<arg2>|...)'
    """
    return '({})'.format('|'.join(args))


#: Template string to match text exactly (start-to-end)
exact_template = r'^{}$'
#: Template string to match text surrounded by word boundaries
word_template = r'\b{}\b'
quoted_string_template = r'(?<![{0}\w]){0}[^{0}]*{0}(?![{0}\w])'


def exact_match(string):
    """Return regex that matches the input string exactly.

    The returned value is equivalent to writing::

        r'^<string>$'
    """
    return exact_template.format(string)


def bounded_word(string):
    """Return regex that matches the input string as a bounded word.

    The returned value is equivalent to writing::

        r'\\b<string>\\b'
    """
    return word_template.format(string)


#: Pattern matching any text
anything = r'.*'
#: Pattern matching any whitespace
whitespace = r'\s*'
#: Pattern matching start of string
start = r'^'
#: Pattern matching indent at start of string
indent = start + whitespace
#: Pattern matching first word
first_word = indent + r'\w+'

#: Pattern matching floating point number
num_float = bounded_word(r'[+-]?(\d*[.])?\d+')
#: Pattern matching integers
num_int = bounded_word(r'[+-]?\d')
#: Pattern matching integers or floats
number = any_of(num_int, num_float)

#: Pattern matching a numeric year
year = r'\d{4}'
#: Pattern matching a numeric month
month = r'\d{2}'
#: Pattern matching a numeric day
day = r'\d{2}'

#: Pattern matching calendar dates in ISO 8601 format (`YYYY-MM-DD`)
date = bounded_word(r'{}-{}-{}'.format(year, month, day))
#: Pattern matching numeric time
time = bounded_word(r'(\d{2}:\d{2}(:\d{2})?)')
#: Pattern matching numeric time with milliseconds
time_ms = bounded_word(r'\d{2}:\d{2}:\d{2}(,|.)\d{3}')

#: Pattern matching strings surrounded by single-quotes
single_quoted_strings = quoted_string_template.format("'")
#: Pattern matching strings surrounded by double-quotes
double_quoted_strings = quoted_string_template.format('"')
#: Pattern matching strings surrounded by single- or double-quotes
strings = any_of(single_quoted_strings, double_quoted_strings)

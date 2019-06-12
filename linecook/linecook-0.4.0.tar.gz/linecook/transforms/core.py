# -*- coding: utf-8 -*-
"""
Text formatters match the signature of basic regex functions, taking a
text/regex match pattern and an input string.
"""
from __future__ import unicode_literals

import functools
import os

from termcolor import colored
from toolz.functoolz import identity

from .. import patterns
from ..parsers import resolve_match_pattern


def filter_line(match_pattern, on_match=None, on_mismatch=None):
    """Return transform that filters lines by match pattern.

    If neither `on_match` or `on_mismatch` are given, return input
    string if it matches the given pattern. Otherwise, the input string is
    passed to those callback functions and the output is returned.

    Args:
        on_match (callable): A text transform that is called with the input
            `string` if the string matches the `match_pattern`.
        on_mismatch (callable): A text transform that is called with the input
            `string` if the string does not match the `match_pattern`.
    """
    match_pattern = resolve_match_pattern(match_pattern)

    def transform(string):
        match = match_pattern.search(string)

        if not (on_match or on_mismatch):
            return None if match else string

        if match and on_match:
            return on_match(string)
        elif not match and on_mismatch:
            return on_mismatch(string)

    return transform


def partition(match_pattern, on_match=None, on_mismatch=None):
    """Return line partitioned by pattern and re-joined after transformation.

    Args:
        on_match (callable): A text transform that is called with each
            substring that matches the `match_pattern`.
        on_mismatch (callable): A text transform that is called with each
            substring that does not match the `match_pattern`.
    """
    match_pattern = resolve_match_pattern(match_pattern)
    on_match = on_match or identity
    on_mismatch = on_mismatch or identity

    def transform(string):
        i_start = 0
        substrings = []
        for match in match_pattern.finditer(string):
            match_start, match_end = match.span()

            if i_start < match_start:
                substrings.append(on_mismatch(string[i_start:match_start]))

            substrings.append(on_match(string[match_start:match_end]))
            i_start = match_end

        if i_start < len(string):
            substrings.append(on_mismatch(string[i_start:]))

        return ''.join(substrings)

    return transform


def replace_text(match_pattern, replacement):
    match_pattern = resolve_match_pattern(match_pattern)

    def transform(string):
        return match_pattern.sub(replacement, string)

    return transform


def _create_color_replacement(color=None, on_color=None, attrs=None):
    """Return color function used as argument to `re.sub`.

    `re.sub` accepts a function for string replacement, where the match object
    is passed in as the only argument.

    Args:
        color (str): Text color. Any of the following values
            grey, red, green, yellow, blue, magenta, cyan, white.
        on_color (str): Background color. Any of the following values
            on_grey, on_red, on_green, on_yellow, on_blue, on_magenta,
            on_cyan, on_white

        attrs (str): Text attributes. Any of the following values:
            bold, dark, underline, blink, reverse, concealed.
    """
    def color_replacement(match_string):
        if hasattr(match_string, 'group'):
            match_string = match_string.group()
        return colored(match_string, color=color,
                       on_color=on_color, attrs=attrs)
    return color_replacement


def color_text(match_pattern=patterns.anything,
               color=None, on_color=None, attrs=None):
    """Return color transform that returns colorized version of input string.

    Args:
        color (str): Text color. Any of the following values
            grey, red, green, yellow, blue, magenta, cyan, white.
        on_color (str): Background color. Any of the following values
            on_grey, on_red, on_green, on_yellow, on_blue, on_magenta,
            on_cyan, on_white

        attrs (list(str)): Text attributes. Any of the following values:
            bold, dark, underline, blink, reverse, concealed.
    """
    color_replacement = _create_color_replacement(
        color=color, on_color=on_color, attrs=attrs,
    )
    return replace_text(match_pattern, replacement=color_replacement)


class CountLines(object):
    """Tranformation returning line of text with line count added."""

    def __init__(self, line_template='{count_label} {line}',
                 count_template='{count:>3}:',
                 color_kwargs={'color': 'grey', 'attrs': ['bold']}):
        self.count = 0
        self.line_template = line_template
        self.count_template = count_template
        self.color_kwargs = color_kwargs

    def __call__(self, line):
        self.count += 1
        count_label = self.count_template.format(count=self.count)
        count_label = colored(count_label, **self.color_kwargs)
        return self.line_template.format(count_label=count_label, line=line)

    def reset(self):
        self.count = 0


delete_text = functools.partial(replace_text, replacement='')
split_on = functools.partial(replace_text, replacement=os.linesep)

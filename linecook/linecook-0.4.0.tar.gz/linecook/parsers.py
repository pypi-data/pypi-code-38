# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import re

from . import patterns


TYPE_PREFIX_SEPARATOR = ':'

REGEX_WRAPPERS = {
    'exact': patterns.exact_template,
    'word': patterns.word_template,
}

COMPILED_REGEX_TYPE = type(re.compile('^$'))


def create_regex_factory(format_string=None, regex_type=None,
                         ignore_case=False):
    """Return a `create_regex` function that compiles a pattern to a regex."""
    if regex_type:
        format_string = REGEX_WRAPPERS.get(regex_type)
        if not format_string:
            raise KeyError("Unknown regex wrapper: {}".format(regex_type))

    flags = 0
    if ignore_case:
        flags |= re.IGNORECASE

    if format_string:
        def create_regex(pattern):
            return re.compile(format_string.format(pattern), flags=flags)
    else:
        def create_regex(pattern):
            return re.compile(pattern, flags=flags)

    return create_regex


REGEX_FORMATTERS = {
    'exact': create_regex_factory(regex_type='exact'),
    'iexact': create_regex_factory(regex_type='exact', ignore_case=True),
    'word': create_regex_factory(regex_type='word'),
    'iword': create_regex_factory(regex_type='word', ignore_case=True),
}

REGEX_FORMATTERS.update({
    alias: REGEX_FORMATTERS[key] for alias, key in [
        ('x', 'exact'),
        ('xi', 'iexact'),
        ('w', 'word'),
        ('wi', 'iword'),
    ]
})


def resolve_match_pattern(pattern):
    """Return a compiled regex, parsing known regex shorthands."""
    if isinstance(pattern, COMPILED_REGEX_TYPE):
        return pattern

    if TYPE_PREFIX_SEPARATOR in pattern:
        formatter_code, pattern_text = pattern.split(TYPE_PREFIX_SEPARATOR, 1)
        create_regex = REGEX_FORMATTERS.get(formatter_code)
        if create_regex:
            return create_regex(pattern_text)

    return re.compile(pattern)

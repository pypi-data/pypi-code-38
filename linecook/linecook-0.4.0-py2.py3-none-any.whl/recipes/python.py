
# -*- coding: utf-8 -*-
"""
Example of linecook recipe for python code.

This is a toy example: Actual syntax highlighting isn't possible since linecook
doesn't (easily) store state between different lines, which prevents proper
highlighting of things like multi-line strings.
"""
from __future__ import unicode_literals

from toolz.functoolz import compose

from .. import patterns
from ..transforms import color_text, CountLines, partition


PYTHON_KEYWORDS = (
    r"w:(False|class|finally|is|return|None|continue|for|lambda|try|True|def|"
    r"from|nonlocal|while|and|del|global|not|with|as|elif|if|or|yield|assert|"
    r"else|import|pass|break|except|in|raise)"
)

recipe = [
    partition(
        patterns.strings,
        on_match=color_text('.*', color='yellow'),
        on_mismatch=compose(
            color_text(PYTHON_KEYWORDS, color='red'),
            color_text(patterns.number, color='cyan'),
        ),
    ),
    CountLines(),
]

"""Jinja2 environment"""

import math
import re
import textwrap

import humanize.number
import humanize.time
import jinja2

__all__ = ('env',)

env = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__, 'templates'),
    # The options below are suggested by the Chromium Jinja style guide,
    # https://www.chromium.org/developers/jinja.
    keep_trailing_newline=True,  # newline-terminate generated files
    lstrip_blocks=True,  # so can indent control flow tags
    trim_blocks=True,  # so don't need {%- -%} everywhere
    extensions=['jinja2.ext.loopcontrols']
)

_rewrap_regex = re.compile(
    r'^[ \t]+.+\n|([^ \t\n]+[^\n]*\n)+|.*',
    flags=re.MULTILINE)


def rewrap(text):
    """Rewrap the given text, paragraph by paragraph. Treat any line that begins
    with whitespace as a separate paragraph, and any consecutive sequence of
    lines that do not begin with whitespace as a paragraph."""
    return '\n'.join(textwrap.fill(text[match.start():match.end()])
                     for match in _rewrap_regex.finditer(text))


env.filters['log10'] = math.log10
env.filters['rewrap'] = rewrap
env.filters['apnumber'] = humanize.number.apnumber
env.filters['naturaldelta'] = humanize.time.naturaldelta

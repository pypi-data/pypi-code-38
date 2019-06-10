""" Module used to perform Consistency Checks using XRootD.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

# We want everything logged nicely
from . import logsetup

from ._version import __version__

from .parser import OPTS as opts
from .parser import ARGS as args

from .parser import get_parser

# Make sure all of the possible opts are filled
_PARSER, _ = get_parser(prog='exec.py')
_HAVE = set(dir(opts))

for opt in _PARSER.option_list + \
        [opt for group in _PARSER.option_groups for opt in group.option_list]:
    attr = opt.dest
    if attr and attr not in _HAVE:
        setattr(opts, attr, None)

__all__ = []

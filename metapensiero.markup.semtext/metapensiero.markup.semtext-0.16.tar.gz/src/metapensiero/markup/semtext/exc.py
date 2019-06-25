# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- Exceptions
# :Created:   sab 01 apr 2017 13:22:47 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

from .ast import Paragraph, Span, Text


class UnparsableError(ValueError):
    "Error raised when something goes wrong within the SEM parser"

    @property
    def message(self):
        "The error message"
        return self.args[0]

    @property
    def text(self):
        "The whole raw text wrapped inside a single paragraph"
        return Text([Paragraph([Span(self.args[1])])])


class InvalidNestingError(ValueError):
    "Error raised when there is a depth mismatch in nested lists."

    def __init__(self, expected, got):
        super().__init__('Invalid nesting, expected %d got %d' % (expected, got))
        self.expected = expected
        self.got = got

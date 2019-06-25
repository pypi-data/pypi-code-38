# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- Simple Enough Markup parser
# :Created:   Wed 23 Nov 2016 09:28:39 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

from logging import getLogger
import sys

from sly import Parser as SlyParser

from .ast import Heading, Item, Link, List, ListStyle, Paragraph, Span, SpanStyle, Text
from .lexer import Lexer


logger = getLogger(__name__)


class Parser(SlyParser):
    "SEMtext parser."

    tokens = Lexer.tokens

    precedence = (
        ('right', 'ITEMS'),
        ('right', 'DOT_ITEM', 'NUM_ITEM'),
    )

    def __init__(self):
        self.errors = []

    def error(self, token):
        self.errors.append(token)
        if token:
            lineno = getattr(token, 'lineno', 0)
            if lineno:
                logger.error('Syntax error at line %d, token=%s'
                             % (lineno, token))
            else:
                logger.error('Syntax error, token=%s' % token)
        else:
            logger.error('Parse error in input: EOF')

    @_('elements')
    def text(self, p):
        return Text(p.elements)

    @_('elements element')
    def elements(self, p):
        return p.elements + [p.element]

    @_('element')
    def elements(self, p):
        return [p.element]

    @_('heading SEPARATOR')
    def element(self, p):
        return p.heading

    @_('paragraph SEPARATOR')
    def element(self, p):
        return p.paragraph

    @_('HEADING_START spans HEADING_STOP')
    def heading(self, p):
        return Heading(p.HEADING_START, p.spans)

    @_('spans')
    def paragraph(self, p):
        return Paragraph(p.spans)

    @_('spans span')
    def spans(self, p):
        return p.spans + [p.span]

    @_('span')
    def spans(self, p):
        return [p.span]

    @_('BOLD_START string BOLD_STOP')
    def span(self, p):
        return Span(p.string, SpanStyle.BOLD)

    @_('ITALIC_START string ITALIC_STOP')
    def span(self, p):
        return Span(p.string, SpanStyle.ITALIC)

    @_('LINK_START string LINK_STOP')
    def span(self, p):
        if '<' in p.string:
            text, address = p.string.split('<', 1)
            if '<' in address or address[-1] != '>':
                raise ValueError('Bad link address: %s' % address)
            text = text.rstrip()
            address = address[:-1].strip()
        else:
            text = p.string
            address = ''
        return Link(text, address)

    @_('string')
    def span(self, p):
        return Span(p.string)

    @_('string NEWLINE TEXT')
    def string(self, p):
        return p.string + ' ' + p.TEXT

    @_('TEXT')
    def string(self, p):
        return p.TEXT

    @_('list')
    def element(self, p):
        return p.list

    @_('dot_items %prec ITEMS')
    def list(self, p):
        return List(p.dot_items)

    @_('num_items %prec ITEMS')
    def list(self, p):
        return List(p.num_items, ListStyle.NUMERIC)

    @_('dot_items dot_item')
    def dot_items(self, p):
        return p.dot_items + [p.dot_item]

    @_('dot_item')
    def dot_items(self, p):
        return [p.dot_item]

    @_('DOT_ITEM sub_elements')
    def dot_item(self, p):
        return Item(p.sub_elements)

    @_('num_items num_item')
    def num_items(self, p):
        return p.num_items + [p.num_item]

    @_('num_item')
    def num_items(self, p):
        return [p.num_item]

    @_('NUM_ITEM sub_elements')
    def num_item(self, p):
        return Item(p.sub_elements, p.NUM_ITEM)

    @_('INDENT elements DEDENT')
    def sub_elements(self, p):
        return p.elements


if __name__ == '__main__': # pragma: nocover
    from .visitor import ASTPrinter

    data = """\
Lorem ipsum *dolor* sit amet,
1 * 2 /consectetur/ adipisicing elit,
2 / 3 sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua.

Ut enimad minim *veniam, quis nostrud exercitation
ullamco laboris* nisi ut aliquip ex ea commodo consequat.

Duis aute irure /dolor in reprehenderit in voluptate
velit esse cillum/ *dolore* eu fugiat nulla pariatur.

Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia deserunt mollit anim id est laborum.

- Foo
  Bar

- Bar

  Bar

  Bar

- Bah

  ciò

  1. X

  2. Y
"""

    data = """\
This is *just* a tiny /test/:

1. One

2. Two

   Two and half

   - Foo

   - Bar

Whoa!
"""
    if len(sys.argv) > 1:
        print('Enter text to be parsed, terminate with ^D:')
        data = sys.stdin.read()[:-1]

    lexer = Lexer()
    lexed = lexer.tokenize(data)

    parser = Parser()
    parsed = parser.parse(lexed)

    ASTPrinter().visit(parsed)

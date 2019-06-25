# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- Simple Enough Markup lexer
# :Created:   Wed 23 Nov 2016 09:14:23 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Arstecnica s.r.l.
# :Copyright: © 2018, 2019 Lele Gaifax
#

import re
import sys

from sly.lex import Lexer as SlyLexer, Token


PREFIX_RX = re.compile(r'\s+')
NUM_ITEM_RX = re.compile(r'(\d+)[.)] ')
DOT_ITEM_RX = re.compile(r'[-*] ')
SPAN_RX = re.compile(r'''
    (?P<url>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)
    |
    (?P<start>
        ((?<=\s)|(?<=\A))   # preceded by a space, or at the beginning
        [*/`]               # a style marker
        (?!\s)              # followed by a non-space
    )
    |
    (?P<stop>
        (?<!\s)             # preceded by a non-space
        [*/`]               # a style marker
        ((?=\W)|(?=\Z))     # a non-word character, or at the end
    )
    ''', re.VERBOSE)
HEADING_RX = re.compile(r'''
    (?P<heading>
        (?<=\A)
        =+
    )
    \s+
    (?P<text> .+)
    \s+
    (?P=heading)            # same number of '='
    \s*
    (?=\Z)
    ''', re.VERBOSE)


class SemError(ValueError):
    "Error raised on invalid SEM markup"

    @property
    def message(self):
        "The error message"
        return self.args[0]

    @property
    def position(self):
        "The error position, a tuple with line and column number"
        return self.args[1]


class Lexer(SlyLexer):
    tokens = {
        'TEXT',
        'HEADING_START',
        'HEADING_STOP',
        'BOLD_START',
        'BOLD_STOP',
        'ITALIC_START',
        'ITALIC_STOP',
        'LINK_START',
        'LINK_STOP',
        'NEWLINE',
        'SEPARATOR',
        'INDENT',
        'DEDENT',
        'DOT_ITEM',
        'NUM_ITEM',
    }

    @_(r'\n\s*\n+')
    def SEPARATOR(self, t):
        self.lineno += len(t.value)
        return t

    @_(r'\n')
    def NEWLINE(self, t):
        self.lineno += len(t.value)
        return t

    TEXT = r'.+'

    def __init__(self):
        super().__init__()
        self._indents = [self._token('INDENT', 0, 0, 0)]
        self._last_span_start = None

    def _token(self, type, value, lineno=None, index=None):
        token = Token()
        token.type = type
        token.value = value
        token.lineno = self.lineno if lineno is None else lineno
        token.index = self.index if index is None else index
        return token

    def _column(self, text, index):
        last_cr = text.rfind('\n', 0, index)
        if last_cr < 0:
            last_cr = 0
        column = (index - last_cr) + 1
        return column

    def _push_indent(self, amount, index):
        current = self._indents[-1].value
        indent = self._token('INDENT', current+amount, index=index)
        self._indents.append(indent)
        return indent

    def _handle_prefix(self, token):
        text = token.value
        prefix = PREFIX_RX.match(text)
        amount = 0 if prefix is None else prefix.end()
        current = self._indents[-1].value
        if amount > current:
            yield self._push_indent(amount, token.index)
        else:
            while amount < current:
                self._indents.pop()
                current = self._indents[-1].value
                yield self._token('DEDENT', current)
            if amount != current:
                pos = (self.lineno, self._column(self._text, token.index))
                raise SemError('Mismatched indent at line %d' % self.lineno, pos)
        token.value = text[amount:]
        token.index += amount

    def _handle_item(self, token):
        text = token.value
        prefix = DOT_ITEM_RX.match(text)
        if prefix is not None:
            yield self._token('DOT_ITEM', '*')
            amount = prefix.end()
            yield self._push_indent(amount, index=self.index + amount)
            token.value = text[amount:]
            token.index += amount
        else:
            prefix = NUM_ITEM_RX.match(text)
            if prefix is not None:
                yield self._token('NUM_ITEM', int(prefix.group(1)))
                amount = prefix.end()
                yield self._push_indent(amount, index=self.index + amount)
                token.value = text[amount:]
                token.index += amount

    def _split_spans(self, token):
        text = token.value
        index = token.index
        last_point = 0
        for span in SPAN_RX.finditer(text):
            if span.lastgroup == 'url':
                continue
            start, stop = span.span()
            if start != last_point:
                yield self._token('TEXT', text[last_point:start],
                                  index=index+last_point)
            if span.lastgroup == 'start':
                if span.group() == '*':
                    if self._last_span_start is not None:
                        pos = (self.lineno,
                               self._column(self._text, index+start))
                        lss = self._last_span_start
                        msg = ('%s span already started at line %d column %d'
                               % (lss.type.lower(), lss.lineno,
                                  self._column(self._text, lss.index)))
                        raise SemError('Overlapped bold_start at line %d: %s'
                                       % (self.lineno, msg), pos)
                    tok = self._token('BOLD_START', '*', index=index+start)
                elif span.group() == '/':
                    if self._last_span_start is not None:
                        pos = (self.lineno,
                               self._column(self._text, index+start))
                        lss = self._last_span_start
                        msg = ('%s span already started at line %d column %d'
                               % (lss.type.lower(), lss.lineno,
                                  self._column(self._text, lss.index)))
                        raise SemError('Overlapped italic_start at line %d: %s'
                                       % (self.lineno, msg), pos)
                    tok = self._token('ITALIC_START', '/', index=index+start)
                else:
                    if self._last_span_start is not None:
                        pos = (self.lineno,
                               self._column(self._text, index+start))
                        lss = self._last_span_start
                        msg = ('%s span already started at line %d column %d'
                               % (lss.type.lower(), lss.lineno,
                                  self._column(self._text, lss.index)))
                        raise SemError('Overlapped link_start at line %d: %s'
                                       % (self.lineno, msg), pos)
                    tok = self._token('LINK_START', '`', index=index+start)

                yield tok
                self._last_span_start = tok
            else:
                if span.group() == '*':
                    if self._last_span_start is None:
                        pos = (self.lineno,
                               self._column(self._text, index+start))
                        raise SemError('Unpaired bold_stop at line %d'
                                       % self.lineno, pos)
                    tok = self._token('BOLD_STOP', '*', index=index+start)
                elif span.group() == '/':
                    if self._last_span_start is None:
                        pos = (self.lineno,
                               self._column(self._text, index+start))
                        raise SemError('Unpaired italic_stop at line %d'
                                       % self.lineno, pos)
                    tok = self._token('ITALIC_STOP', '/', index=index+start)
                else:
                    if self._last_span_start is None:
                        pos = (self.lineno,
                               self._column(self._text, index+start))
                        raise SemError('Unpaired link_stop at line %d'
                                       % self.lineno, pos)
                    tok = self._token('LINK_STOP', '`', index=index+start)
                yield tok
                self._last_span_start = None
            last_point = stop

        if self._last_span_start:
            lss = self._last_span_start
            pos = (self.lineno, self._column(self._text, lss.index))
            raise SemError('Unpaired %s at line %d column %d'
                           % (lss.type.lower(), pos[0], pos[1]), pos)

        token.value = text[last_point:]
        token.index += last_point

    def _handle_heading(self, token, heading):
        level = len(heading.group('heading'))
        yield self._token('HEADING_START', level)
        token.value = heading.group('text')
        token.index = heading.start('text')
        yield from self._split_spans(token)
        if token.value:
            yield token
        yield self._token('HEADING_STOP', level, index=heading.endpos - level)

    def tokenize(self, text, lineno=1, index=0):
        self.lineno = lineno
        self.index = index
        self._text = text
        for token in super().tokenize(text+'\n\n', lineno, index):
            if token.type == 'TEXT':
                heading = HEADING_RX.match(token.value)
                if heading:
                    yield from self._handle_heading(token, heading)
                    continue
                else:
                    yield from self._handle_prefix(token)
                    yield from self._handle_item(token)
                    yield from self._split_spans(token)
            if token.value:
                yield token

        while len(self._indents) > 1:
            self._indents.pop()
            current = self._indents[-1].value
            yield self._token('DEDENT', current)


if __name__ == '__main__':  # pragma: nocover
    data = """\
= Title =

Lorem ipsum *dolor* sit amet,
1 * 2 /consectetur/ adipisicing elit,
2 / 3 sed do eiusmod tempor incididunt /ut/
labore et dolore magna aliqua.

Ut enimad minim *veniam, quis nostrud exercitation
ullamco laboris* nisi ut `aliquip <ex>` ea commodo consequat.

*Duis* aute irure /dolor in reprehenderit in voluptate
velit esse cillum/ *dolore* eu fugiat nulla pariatur.

Excepteur sint occaecat cupidatat non proident,
   sunt in culpa qui officia deserunt mollit anim id est laborum.

- Foo
  Ahh

- Bar

- Boh

  1. cippa
  2. lippa
  3. ouch
"""

    if len(sys.argv) > 1:
        print('Enter text to be lexed, terminate with ^D:')
        data = sys.stdin.read()[:-1]

    lexer = Lexer()
    for tok in lexer.tokenize(data):
        print(tok)

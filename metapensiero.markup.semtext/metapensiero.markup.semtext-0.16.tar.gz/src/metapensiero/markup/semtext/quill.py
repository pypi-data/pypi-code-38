# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- Quill related stuff
# :Created:   ven 28 lug 2017 17:58:16 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

from .ast import Heading, Item, Link, List, ListStyle, Paragraph, Span, SpanStyle, Text
from .exc import InvalidNestingError


def simplify(ops):
    "Simplify the stream, generating standalone `end-of-paragraph` markers."

    start = True
    for op in ops:
        text = op['insert']
        if text.startswith('\n') and text != '\n':
            if not start:
                yield {'insert': '\n'}
            text = text.lstrip('\n')
        start = False
        eop = text.endswith('\n')
        text = text.rstrip('\n')
        chunks = text.split('\n')
        for chunk in chunks[:-1]:
            if chunk:
                yield {'insert': chunk}
                yield {'insert': '\n'}
        tail = {'insert': chunks[-1]}
        if 'attributes' in op:
            tail['attributes'] = op['attributes']
        yield tail
        if eop:
            yield {'insert': '\n'}


def minimize_span(kind, text):
    "Separate whitespaces on the edge of text into single space events."

    if text.startswith(' '):
        text = text.lstrip()
        yield 'plain', ' '
    if text.endswith(' '):
        yield kind, text.rstrip()
        yield 'plain', ' '
    else:
        yield kind, text


def minimize_link(text, address):
    "Separate whitespaces on the edge of text into single space events."

    if text.startswith(' '):
        text = text.lstrip()
        yield 'plain', ' '
    if text.endswith(' '):
        yield 'link', (text.rstrip(), address)
        yield 'plain', ' '
    else:
        yield 'link', (text, address)


def minimize_spans(ops):
    "Replace text with attributes with equivalent minimized spans."

    for op in simplify(ops):
        text = op['insert']
        attrs = op.get('attributes')
        if attrs is None:
            yield 'plain', text
        else:
            if attrs.get('bold'):
                yield from minimize_span('bold', text)
            elif attrs.get('italic'):
                yield from minimize_span('italic', text)
            elif attrs.get('link'):
                yield from minimize_link(text, attrs.get('link'))
            else:
                yield op


def itemize(ops):
    "Replace list events with equivalent items."

    for op in minimize_spans(ops):
        if isinstance(op, tuple):
            yield op
        else:
            text = op['insert']
            attrs = op.get('attributes')
            lst = attrs.get('list')
            if lst is not None:
                yield 'plain', text
                yield lst, attrs.get('indent', 0)
            else:
                header = attrs.get('header')
                if header is not None:
                    yield 'header', header
                else:
                    raise NotImplementedError('Got %r' % attrs)


def reduce_paragraphs(ops):
    """Group consecutive span events into equivalent :class:`~.ast.Paragraph`
    containing :class:`~.ast.Span` instances.
    """

    spans = []
    for kind, value in itemize(ops):
        if kind == 'plain':
            if value == '\n':
                if spans:
                    yield Paragraph(spans)
                    spans = []
            else:
                spans.append(Span(value))
        elif kind == 'bold':
            spans.append(Span(value, SpanStyle.BOLD))
        elif kind == 'italic':
            spans.append(Span(value, SpanStyle.ITALIC))
        elif kind == 'link':
            spans.append(Link(value[0], value[1]))
        else:
            if spans:
                yield Paragraph(spans)
                spans = []
            yield kind, value

    if spans:
        yield Paragraph(spans)


def from_delta(contents):
    """Transform a Quill's delta__ `contents` into the equivalent *AST*.

    :param contents: a dictionary containing ``ops``, a list of delta's events
    :returns: a :class:`~.ast.Text` instance with the (*almost*) equivalent
              *SEM AST*

    __ https://quilljs.com/docs/delta/
    """

    # Stack of currently active lists: each element is a tuple of (kind,
    # list-items)
    lists = []

    # The elements collected so far
    elts = []

    for elt in reduce_paragraphs(contents['ops']):
        if isinstance(elt, tuple):
            # A header with its level, or a list item, carrying its list type and depth
            assert elts
            # Remove last collected element, should be either a Paragraph or a
            # List
            tip = elts.pop()
            assert isinstance(tip, (Paragraph, List))
            kind, level = elt
            if kind == 'header':
                elts.append(Heading(level, tip.children))
            elif not lists:
                # No active lists: create new one
                assert level == 0
                lstelts = [Item([tip])]
                lst = List(lstelts,
                           ListStyle.DOTTED if kind == 'bullet'
                           else ListStyle.NUMERIC)
                lists.append((kind, lstelts))
                elts.append(lst)
            elif level+1 == len(lists):
                # Item at the same depth of the list at the top of the stack:
                # if it is of the same kind it to its elements, otherwise
                # terminate that and create a new one
                if kind == lists[-1][0]:
                    lists[-1][1].append(Item([tip]))
                else:
                    lists.pop()
                    lstelts = [Item([tip])]
                    lst = List(lstelts,
                               ListStyle.DOTTED if kind == 'bullet'
                               else ListStyle.NUMERIC)
                    lists.append((kind, lstelts))
                    elts.append(lst)
            elif level+1 > len(lists):
                # Item at a deeper level: create a new list and append it to
                # the children of the last item of the list at ToS
                if level != len(lists):
                    raise InvalidNestingError(len(lists), level)
                assert level == len(lists)
                lstelts = [Item([tip])]
                lst = List(lstelts,
                           ListStyle.DOTTED if kind == 'bullet'
                           else ListStyle.NUMERIC)
                lists.append((kind, lstelts))
                tip = elts[-1]
                assert isinstance(tip, List)
                tip.children[-1].children.append(lst)
            else:
                # Item at a higher level than the list at ToS: remove deeper
                # lists, then if the item is of the same kind of the remaining
                # list in the stack otherwise create a new one
                lists = lists[:level+1]
                if kind == lists[-1][0]:
                    lists[-1][1].append(Item([tip]))
                else:
                    lists.pop()
                    lstelts = [Item([tip])]
                    lst = List(lstelts,
                               ListStyle.DOTTED if kind == 'bullet'
                               else ListStyle.NUMERIC)
                    lists.append((kind, lstelts))
                    elts.append(lst)
        else:
            # Two paragraphs in a row means terminate existing lists
            if elts and isinstance(elt, type(elts[-1])):
                lists = []
            elts.append(elt)

    return Text(elts)


def to_delta(ast):
    "Return a Quill Delta equivalent to the `ast`."

    from .visitor import DeltaPrinter

    printer = DeltaPrinter()
    printer.visit(ast)
    return {'ops': printer.ops}

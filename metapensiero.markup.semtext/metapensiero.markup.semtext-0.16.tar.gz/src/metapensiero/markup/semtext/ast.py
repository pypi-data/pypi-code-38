# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- Abstract Syntax Tree nodes
# :Created:   mer 23 nov 2016 10:20:10 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

from enum import Enum


class SpanStyle(Enum):
    "Various kinds of spans."

    PLAIN = 0
    "Undecorated text."

    BOLD = 1
    "Bold text."

    ITALIC = 2
    "Italic text."


class ListStyle(Enum):
    "Various kinds of lists"

    DOTTED = 0
    "Unordered list."

    NUMERIC = 1
    "Ordered list."


class Node(object):
    "Base common class."

    def __init__(self, children):
        self.children = children


class Text(Node):
    """
    The whole thing, composed by multiple :class:`paragraphs <.Paragraph>`,
    :class:`headings <.Heading>` and :class:`lists <.List>`.
    """


class Paragraph(Node):
    """
    A single paragraph, composed by multiple :class:`spans <.Span>` of text.
    """

    def __init__(self, children):
        children[0].text = children[0].text.lstrip()
        while children:
            children[-1].text = children[-1].text.rstrip()
            if len(children) > 1 and not children[-1].text:
                children.pop()
            else:
                break
        super().__init__(children)


class Heading(Paragraph):
    """
    A section title, of a particular level.
    """

    def __init__(self, level, children):
        self.level = level
        super().__init__(children)


class Span(object):
    "A single span of text, with some :class:`style <.SpanStyle>`."

    def __init__(self, text, style=SpanStyle.PLAIN):
        self.text = text
        self.style = style


class List(Node):
    "A single list of :class:`items <.Item>`."

    def __init__(self, children, style=ListStyle.DOTTED):
        self.style = style
        super().__init__(children)


class Item(Text):
    "A single list item, that may contain a whole text."

    def __init__(self, children, index=None):
        self.index = index
        super().__init__(children)


class Link(Span):
    "An hyperlink."

    def __init__(self, text, address):
        if not text or not text.strip():
            text = address
        super().__init__(text)
        self.address = address

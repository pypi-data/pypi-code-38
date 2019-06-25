# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- HTML parser
# :Created:   sab 01 apr 2017 14:00:33 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Arstecnica s.r.l.
# :Copyright: © 2018, 2019 Lele Gaifax
#

from io import StringIO
from logging import getLogger
from re import compile

from lxml.etree import HTMLParser, parse
from lxml.html import fragment_fromstring

from .ast import Heading, Item, Link, List, ListStyle, Paragraph, Span, SpanStyle, Text
from .text import parse_text
from .visitor import HTMLPrinter, SEMPrinter


logger = getLogger(__name__)


def squash_ws(text, empty=None, ws_rx=compile(r'\s+')):
    "Squash consecutive whitespaces to a single space."

    if not text:
        return None
    elif text.isspace():
        return empty
    else:
        return ws_rx.sub(" ", text)


FACTORIES = {}


def tag_factory(cls):
    FACTORIES[cls.TAG] = cls
    return cls


class BaseFactory:
    @classmethod
    def install(cls, parent, attrib):
        while not (parent.accepts_sibling_class(cls) and cls.accepts_parent(parent)):
            parent.sibling = None
            parent()
            parent = parent.parent
        parent.sibling = cls(parent, attrib)
        return parent

    def accepts_sibling_class(self, sibling_class):
        return True

    @classmethod
    def accepts_parent(cls, parent):
        return True

    def __init__(self, parent, attrib):
        self.parent = parent
        self._sibling = None

    def _get_sibling(self):
        return self._sibling

    def _set_sibling(self, value):
        if self._sibling is not None:
            self._sibling()
        self._sibling = value

    sibling = property(_get_sibling, _set_sibling)

    def comment(self, text):
        pass

    def data(self, data):
        raise NotImplementedError('Method "%s.data" not implemented!'
                                  % (self.__class__.__name__))

    def __call__(self):
        raise NotImplementedError('Method "%s.__call__" not implemented!'
                                  % (self.__class__.__name__))


class ScalarFactory(BaseFactory):
    def end(self, tag):
        self()


class ContainerFactory(BaseFactory):
    def __init__(self, parent, attrib):
        super().__init__(parent, attrib)
        self.nodes = []

    @property
    def leaf_container(self):
        leaf = self
        while leaf.sibling is not None and isinstance(leaf.sibling, ContainerFactory):
            leaf = leaf.sibling
        return leaf

    def data(self, data):
        if data and not (data.startswith(('\n', '\r')) and data.isspace()):
            self.sibling.data(data)


class BaseParagraphFactory(ContainerFactory):
    def __init__(self, parent, attrib):
        super().__init__(parent, attrib)
        self.spans = []

    def data(self, data):
        if self.sibling is None:
            PlainSpanFactory.install(self, {})
        self.sibling.data(data)

    def _collapsed_spans(self):
        spans = self.spans
        if not spans:
            return spans
        pchild = spans.pop(0)
        while spans and squash_ws(pchild.text) is None:
            pchild = spans.pop(0)
        collapsed = [pchild]
        add = collapsed.append
        while spans:
            nchild = spans.pop(0)
            if type(pchild) is type(nchild) and pchild.style == nchild.style:
                pchild.text = squash_ws(pchild.text + nchild.text)
            else:
                add(nchild)
                pchild = nchild
        collapsed = list(filter(lambda s: s.text, collapsed))
        while collapsed and squash_ws(collapsed[-1].text) is None:
            collapsed.pop()
        return collapsed

    def _break(self):
        sibling_class = type(self.sibling)
        self.sibling = None
        spans = self._collapsed_spans()
        if spans:
            self.nodes.append(Paragraph(spans))
            if issubclass(sibling_class, SpanFactory):
                sibling_class.install(self, None)


@tag_factory
class ParagraphFactory(BaseParagraphFactory):
    TAG = 'p'

    def accepts_sibling_class(self, sibling):
        return issubclass(sibling, (SpanFactory, LinkFactory))

    @classmethod
    def accepts_parent(cls, parent):
        if isinstance(parent, ItemFactory):
            parent._break()
        return super().accepts_parent(parent)

    def __call__(self):
        spans = self._collapsed_spans()
        if spans:
            self.nodes.append(Paragraph(spans))
        if self.nodes:
            self.parent.nodes.extend(self.nodes)
            self.nodes = []


class HeadingFactory(BaseParagraphFactory):
    def __init__(self, parent, attrib, level):
        super().__init__(parent, attrib)
        self.level = level

    def __call__(self):
        spans = self._collapsed_spans()
        if spans:
            self.nodes.append(Heading(self.level, spans))
        if self.nodes:
            self.parent.nodes.extend(self.nodes)
            self.nodes = []

    def _break(self):
        sibling_class = type(self.sibling)
        self.sibling = None
        spans = self._collapsed_spans()
        if spans:
            self.nodes.append(Heading(self.level, spans))
            if issubclass(sibling_class, SpanFactory):
                sibling_class.install(self, None)


@tag_factory
class H1Factory(HeadingFactory):
    TAG = 'h1'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, 1)


@tag_factory
class H2Factory(HeadingFactory):
    TAG = 'h2'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, 2)


@tag_factory
class H3Factory(HeadingFactory):
    TAG = 'h3'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, 3)


@tag_factory
class H4Factory(HeadingFactory):
    TAG = 'h4'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, 4)


@tag_factory
class H5Factory(HeadingFactory):
    TAG = 'h5'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, 5)


@tag_factory
class H6Factory(HeadingFactory):
    TAG = 'h6'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, 6)


class SpanFactory(ScalarFactory):
    @classmethod
    def install(cls, parent, attrib):
        if not isinstance(parent, BaseParagraphFactory):
            parent = ParagraphFactory.install(parent, None).sibling
        return super().install(parent, attrib)

    def __init__(self, parent, attrib, style):
        super().__init__(parent, attrib)
        self.style = style
        self.text = ''

    def __call__(self):
        if self.text:
            self.parent.spans.append(Span(self.text, self.style))
            self.text = ''

    def data(self, data):
        self.text = squash_ws(self.text + data, empty=" ")


@tag_factory
class PlainSpanFactory(SpanFactory):
    TAG = "span"

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, SpanStyle.PLAIN)


@tag_factory
class BoldSpanFactory(SpanFactory):
    TAG = 'b'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, SpanStyle.BOLD)


@tag_factory
class StrongSpanFactory(BoldSpanFactory):
    TAG = 'strong'


@tag_factory
class ItalicSpanFactory(SpanFactory):
    TAG = 'em'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, SpanStyle.ITALIC)


@tag_factory
class ISpanFactory(ItalicSpanFactory):
    TAG = 'i'


@tag_factory
class BRFactory(BaseFactory):
    TAG = 'br'

    @classmethod
    def install(cls, parent, attrib):
        if hasattr(parent, '_break'):
            parent._break()


@tag_factory
class LinkFactory(BaseParagraphFactory):
    TAG = 'a'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib)
        self.href = attrib.get('href')

    def __call__(self):
        spans = self._collapsed_spans()
        if spans and self.href:
            text = ''.join(s.text for s in spans)
            self.parent.spans.append(Link(text, self.href))


class ListFactory(ContainerFactory):
    def __init__(self, parent, attrib, style):
        super().__init__(parent, attrib)
        self.style = style

    @classmethod
    def accepts_parent(cls, parent):
        if isinstance(parent, ItemFactory):
            parent._break()
        return super().accepts_parent(parent)

    def __call__(self):
        if self.nodes:
            self.parent.nodes.append(List(self.nodes, self.style))
            self.nodes = []


@tag_factory
class DottedListFactory(ListFactory):
    TAG = 'ul'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, ListStyle.DOTTED)


@tag_factory
class NumericListFactory(ListFactory):
    TAG = 'ol'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib, ListStyle.NUMERIC)

    def __call__(self):
        if self.nodes:
            index = 0
            for item in self.nodes:
                if item.index is None:
                    index += 1
                    item.index = index
                else:
                    index = item.index
            self.parent.nodes.append(List(self.nodes, self.style))
            self.nodes = []


@tag_factory
class ItemFactory(BaseParagraphFactory):
    TAG = 'li'

    def __init__(self, parent, attrib):
        super().__init__(parent, attrib)
        value = attrib.get('value')
        if value is not None:
            value = int(value)
        self.index = value

    def __call__(self):
        spans = self._collapsed_spans()
        if spans:
            self.nodes.append(Paragraph(spans))
        if self.nodes:
            self.parent.nodes.append(Item(self.nodes, self.index))
            self.nodes = []


@tag_factory
class ImgFactory(ScalarFactory):
    TAG = 'img'

    def __call__(self):
        pass


@tag_factory
class StyleFactory(ScalarFactory):
    TAG = 'style'

    def data(self, data):
        pass

    def __call__(self):
        pass


class TextFactory(ContainerFactory):
    TAG = 'TEXT'

    def __init__(self):
        super().__init__(None, None)

    def close(self):
        leaf = self.leaf_container
        while leaf is not self:
            leaf.sibling = None
            leaf()
            leaf = leaf.parent
        self.sibling = None
        return Text(self.nodes)

    def start(self, tag, attrib):
        if tag == 'div':
            tag = 'br'
        if tag not in ('body', 'html', 'span'):
            if tag in FACTORIES:
                FACTORIES[tag].install(self.leaf_container, attrib)
            else:
                logger.warning('No factory for tag <%s>, ignoring!' % tag)

    def end(self, tag):
        if tag not in ('body', 'html', 'div', 'br', 'span'):
            if tag in FACTORIES:
                inner = self.leaf_container
                sibling_tag = None
                if inner.sibling is not None:
                    sibling_tag = inner.sibling.TAG
                    inner.sibling = None
                if sibling_tag != tag:
                    while inner.TAG != 'TEXT':
                        inner()
                        inner.parent.sibling = None
                        if inner.TAG == tag:
                            break
                        inner = inner.parent
            else:
                logger.warning('No factory for tag </%s>, ignoring!' % tag)

    def data(self, data):
        if self.sibling is None:
            ParagraphFactory.install(self, {})
        super().data(data)


def parse_html(html, fallback_to_plain_text=True):
    "Parse `html` and return a :class:`.ast.Text` with the equivalent *AST*."

    parser = HTMLParser(target=TextFactory())
    try:
        return parse(StringIO(html), parser)
    except Exception as e:
        if fallback_to_plain_text:
            logger.exception('Could not parse HTML, %s: %r', e, html)
            fragment = fragment_fromstring(html, 'text')
            plain = squash_ws(''.join(fragment.itertext()))
            return Text([Paragraph([Span(plain)])])
        else:
            raise


def html_to_text(html):
    """Parse `html` and return an equivalent *semtext*."""

    if squash_ws(html):
        parsed = parse_html(html)
        stream = StringIO()
        SEMPrinter(where=stream).visit(parsed)
        return stream.getvalue() or html


def text_to_html(text):
    """Parse `text` and return an equivalent ``HTML`` representation."""

    if squash_ws(text):
        parsed = parse_text(text)
        stream = StringIO()
        HTMLPrinter(where=stream).visit(parsed)
        return stream.getvalue() or text

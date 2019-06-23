#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for Dotclear Wiki Syntax
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# XXX: ref used: http://dotclear.org/documentation/2.0/usage/syntaxes#wiki-syntax-and-xhtml-equivalent

from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.constants import Const as C
from sat.core import exceptions
from twisted.words.xish import domish
from sat.tools import xml_tools
import copy
import re

PLUGIN_INFO = {
    C.PI_NAME: "Dotclear Wiki Syntax Plugin",
    C.PI_IMPORT_NAME: "SYNT_DC_WIKI",
    C.PI_TYPE: C.PLUG_TYPE_SYNTAXE,
    C.PI_DEPENDENCIES: ["TEXT_SYNTAXES"],
    C.PI_MAIN: "DCWikiSyntax",
    C.PI_HANDLER: "",
    C.PI_DESCRIPTION: _("""Implementation of Dotclear wiki syntax"""),
}

NOTE_TPL = u"[{}]"  # Note template
NOTE_A_REV_TPL = u"rev_note_{}"
NOTE_A_TPL = u"note_{}"
ESCAPE_CHARS_BASE = r"(?P<escape_char>[][{}%|\\/*#@{{}}~$-])"
ESCAPE_CHARS_EXTRA = (
    r"!?_+'()"
)  # These chars are not escaped in XHTML => dc_wiki conversion,
# but are used in the other direction
ESCAPE_CHARS = ESCAPE_CHARS_BASE.format("")
FLAG_UL = "ul"  # must be the name of the element
FLAG_OL = "ol"
ELT_WITH_STYLE = ("img", "div")  # elements where a style attribute is expected

wiki = [
    r"\\" + ESCAPE_CHARS_BASE.format(ESCAPE_CHARS_EXTRA),
    r"^!!!!!(?P<h1_title>.+?)$",
    r"^!!!!(?P<h2_title>.+?)$",
    r"^!!!(?P<h3_title>.+?)$",
    r"^!!(?P<h4_title>.+?)$",
    r"^!(?P<h5_title>.+?)$",
    r"^----$(?P<horizontal_rule>)",
    r"^\*(?P<list_bullet>.*?)$",
    r"^#(?P<list_ordered>.*?)$",
    r"^ (?P<preformated>.*?)$",
    r"^> +?(?P<quote>.*?)$",
    r"''(?P<emphasis>.+?)''",
    r"__(?P<strong_emphasis>.+?)__",
    r"%%%(?P<line_break>)",
    r"\+\+(?P<insertion>.+?)\+\+",
    r"--(?P<deletion>.+?)--",
    r"\[(?P<link>.+?)\]",
    r"\(\((?P<image>.+?)\)\)",
    r"~(?P<anchor>.+?)~",
    r"\?\?(?P<acronym>.+?\|.+?)\?\?",
    r"{{(?P<inline_quote>.+?)}}",
    r"@@(?P<code>.+?)@@",
    r"\$\$(?P<footnote>.+?)\$\$",
    r"(?P<text>.+?)",
]

wiki_re = re.compile("|".join(wiki), re.MULTILINE | re.DOTALL)
wiki_block_level_re = re.compile(
    r"^///html(?P<html>.+?)///\n\n|(?P<paragraph>.+?)(?:\n{2,}|\Z)",
    re.MULTILINE | re.DOTALL,
)


class DCWikiParser(object):
    def __init__(self):
        self._footnotes = None
        for i in xrange(5):
            setattr(
                self,
                "parser_h{}_title".format(i),
                lambda string, parent, i=i: self._parser_title(
                    string, parent, "h{}".format(i)
                ),
            )

    def parser_paragraph(self, string, parent):
        p_elt = parent.addElement("p")
        self._parse(string, p_elt)

    def parser_html(self, string, parent):
        wrapped_html = "<div>{}</div>".format(string)
        try:
            div_elt = xml_tools.ElementParser()(wrapped_html)
        except domish.ParserError as e:
            log.warning(u"Error while parsing HTML content, ignoring it: {}".format(e))
            return
        children = list(div_elt.elements())
        if len(children) == 1 and children[0].name == "div":
            div_elt = children[0]
        parent.addChild(div_elt)

    def parser_escape_char(self, string, parent):
        parent.addContent(string)

    def _parser_title(self, string, parent, name):
        elt = parent.addElement(name)
        elt.addContent(string)

    def parser_horizontal_rule(self, string, parent):
        parent.addElement("hr")

    def _parser_list(self, string, parent, list_type):
        depth = 0
        while string[depth : depth + 1] == "*":
            depth += 1

        string = string[depth:].lstrip()

        for i in xrange(depth + 1):
            list_elt = getattr(parent, list_type)
            if not list_elt:
                parent = parent.addElement(list_type)
            else:
                parent = list_elt

        li_elt = parent.addElement("li")
        self._parse(string, li_elt)

    def parser_list_bullet(self, string, parent):
        self._parser_list(string, parent, "ul")

    def parser_list_ordered(self, string, parent):
        self._parser_list(string, parent, "ol")

    def parser_preformated(self, string, parent):
        pre_elt = parent.pre
        if pre_elt is None:
            pre_elt = parent.addElement("pre")
        else:
            # we are on a new line, and this is important for <pre/>
            pre_elt.addContent("\n")
        pre_elt.addContent(string)

    def parser_quote(self, string, parent):
        blockquote_elt = parent.blockquote
        if blockquote_elt is None:
            blockquote_elt = parent.addElement("blockquote")
        p_elt = blockquote_elt.p
        if p_elt is None:
            p_elt = blockquote_elt.addElement("p")
        else:
            string = u"\n" + string

        self._parse(string, p_elt)

    def parser_emphasis(self, string, parent):
        em_elt = parent.addElement("em")
        self._parse(string, em_elt)

    def parser_strong_emphasis(self, string, parent):
        strong_elt = parent.addElement("strong")
        self._parse(string, strong_elt)

    def parser_line_break(self, string, parent):
        parent.addElement("br")

    def parser_insertion(self, string, parent):
        ins_elt = parent.addElement("ins")
        self._parse(string, ins_elt)

    def parser_deletion(self, string, parent):
        del_elt = parent.addElement("del")
        self._parse(string, del_elt)

    def parser_link(self, string, parent):
        url_data = string.split(u"|")
        a_elt = parent.addElement("a")
        length = len(url_data)
        if length == 1:
            url = url_data[0]
            a_elt["href"] = url
            a_elt.addContent(url)
        else:
            name = url_data[0]
            url = url_data[1]
            a_elt["href"] = url
            a_elt.addContent(name)
            if length >= 3:
                a_elt["lang"] = url_data[2]
            if length >= 4:
                a_elt["title"] = url_data[3]
            if length > 4:
                log.warning(u"too much data for url, ignoring extra data")

    def parser_image(self, string, parent):
        image_data = string.split(u"|")
        img_elt = parent.addElement("img")

        for idx, attribute in enumerate(("src", "alt", "position", "longdesc")):
            try:
                data = image_data[idx]
            except IndexError:
                break

            if attribute != "position":
                img_elt[attribute] = data
            else:
                data = data.lower()
                if data in ("l", "g"):
                    img_elt["style"] = "display:block; float:left; margin:0 1em 1em 0"
                elif data in ("r", "d"):
                    img_elt["style"] = "display:block; float:right; margin:0 0 1em 1em"
                elif data == "c":
                    img_elt[
                        "style"
                    ] = "display:block; margin-left:auto; margin-right:auto"
                else:
                    log.warning(u"bad position argument for image, ignoring it")

    def parser_anchor(self, string, parent):
        a_elt = parent.addElement("a")
        a_elt["id"] = string

    def parser_acronym(self, string, parent):
        acronym, title = string.split(u"|", 1)
        acronym_elt = parent.addElement("acronym", content=acronym)
        acronym_elt["title"] = title

    def parser_inline_quote(self, string, parent):
        quote_data = string.split(u"|")
        quote = quote_data[0]
        q_elt = parent.addElement("q", content=quote)
        for idx, attribute in enumerate(("lang", "cite"), 1):
            try:
                data = quote_data[idx]
            except IndexError:
                break
            q_elt[attribute] = data

    def parser_code(self, string, parent):
        parent.addElement("code", content=string)

    def parser_footnote(self, string, parent):
        idx = len(self._footnotes) + 1
        note_txt = NOTE_TPL.format(idx)
        sup_elt = parent.addElement("sup")
        sup_elt["class"] = "note"
        a_elt = sup_elt.addElement("a", content=note_txt)
        a_elt["id"] = NOTE_A_REV_TPL.format(idx)
        a_elt["href"] = u"#{}".format(NOTE_A_TPL.format(idx))

        p_elt = domish.Element((None, "p"))
        a_elt = p_elt.addElement("a", content=note_txt)
        a_elt["id"] = NOTE_A_TPL.format(idx)
        a_elt["href"] = u"#{}".format(NOTE_A_REV_TPL.format(idx))
        self._parse(string, p_elt)
        # footnotes are actually added at the end of the parsing
        self._footnotes.append(p_elt)

    def parser_text(self, string, parent):
        parent.addContent(string)

    def _parse(self, string, parent, block_level=False):
        regex = wiki_block_level_re if block_level else wiki_re

        for match in regex.finditer(string):
            if match.lastgroup is None:
                parent.addContent(string)
                return
            matched = match.group(match.lastgroup)
            try:
                parser = getattr(self, "parser_{}".format(match.lastgroup))
            except AttributeError:
                log.warning(u"No parser found for {}".format(match.lastgroup))
                # parent.addContent(string)
                continue
            parser(matched, parent)

    def parse(self, string):
        self._footnotes = []
        div_elt = domish.Element((None, "div"))
        self._parse(string, parent=div_elt, block_level=True)
        if self._footnotes:
            foot_div_elt = div_elt.addElement("div")
            foot_div_elt["class"] = "footnotes"
            # we add a simple horizontal rule which can be customized
            # with footnotes class, instead of a text which would need
            # to be translated
            foot_div_elt.addElement("hr")
            for elt in self._footnotes:
                foot_div_elt.addChild(elt)
        return div_elt


class XHTMLParser(object):
    def __init__(self):
        self.flags = None
        self.toto = 0
        self.footnotes = None  # will hold a map from url to buffer id
        for i in xrange(1, 6):
            setattr(
                self,
                "parser_h{}".format(i),
                lambda elt, buf, level=i: self.parserHeading(elt, buf, level),
            )

    def parser_a(self, elt, buf):
        try:
            url = elt["href"]
        except KeyError:
            # probably an anchor
            try:
                id_ = elt["id"]
                if not id_:
                    # we don't want empty values
                    raise KeyError
            except KeyError:
                self.parserGeneric(elt, buf)
            else:
                buf.append(u"~~{}~~".format(id_))
            return

        link_data = [url]
        name = unicode(elt)
        if name != url:
            link_data.insert(0, name)

        lang = elt.getAttribute("lang")
        title = elt.getAttribute("title")
        if lang is not None:
            link_data.append(lang)
        elif title is not None:
            link_data.appand(u"")
        if title is not None:
            link_data.append(title)
        buf.append(u"[")
        buf.append(u"|".join(link_data))
        buf.append(u"]")

    def parser_acronym(self, elt, buf):
        try:
            title = elt["title"]
        except KeyError:
            log.debug(u"Acronyme without title, using generic parser")
            self.parserGeneric(elt, buf)
            return
        buf.append(u"??{}|{}??".format(unicode(elt), title))

    def parser_blockquote(self, elt, buf):
        # we remove wrapping <p> to avoid empty line with "> "
        children = list(
            [child for child in elt.children if unicode(child).strip() not in ("", "\n")]
        )
        if len(children) == 1 and children[0].name == "p":
            elt = children[0]
        tmp_buf = []
        self.parseChildren(elt, tmp_buf)
        blockquote = u"> " + u"\n> ".join(u"".join(tmp_buf).split("\n"))
        buf.append(blockquote)

    def parser_br(self, elt, buf):
        buf.append(u"%%%")

    def parser_code(self, elt, buf):
        buf.append(u"@@")
        self.parseChildren(elt, buf)
        buf.append(u"@@")

    def parser_del(self, elt, buf):
        buf.append(u"--")
        self.parseChildren(elt, buf)
        buf.append(u"--")

    def parser_div(self, elt, buf):
        if elt.getAttribute("class") == "footnotes":
            self.parserFootnote(elt, buf)
        else:
            self.parseChildren(elt, buf, block=True)

    def parser_em(self, elt, buf):
        buf.append(u"''")
        self.parseChildren(elt, buf)
        buf.append(u"''")

    def parser_h6(self, elt, buf):
        # XXX: <h6/> heading is not managed by wiki syntax
        #      so we handle it with a <h5/>
        elt = copy.copy(elt)  # we don't want to change to original element
        elt.name = "h5"
        self._parse(elt, buf)

    def parser_hr(self, elt, buf):
        buf.append(u"\n----\n")

    def parser_img(self, elt, buf):
        try:
            url = elt["src"]
        except KeyError:
            log.warning(u"Ignoring <img/> without src")
            return

        image_data = [url]

        alt = elt.getAttribute("alt")
        style = elt.getAttribute("style", "")
        desc = elt.getAttribute("longdesc")

        if "0 1em 1em 0" in style:
            position = "L"
        elif "0 0 1em 1em" in style:
            position = "R"
        elif "auto" in style:
            position = "C"
        else:
            position = None

        if alt:
            image_data.append(alt)
        elif position or desc:
            image_data.append(u"")

        if position:
            image_data.append(position)
        elif desc:
            image_data.append(u"")

        if desc:
            image_data.append(desc)

        buf.append(u"((")
        buf.append(u"|".join(image_data))
        buf.append(u"))")

    def parser_ins(self, elt, buf):
        buf.append(u"++")
        self.parseChildren(elt, buf)
        buf.append(u"++")

    def parser_li(self, elt, buf):
        flag = None
        current_flag = None
        bullets = []
        for flag in reversed(self.flags):
            if flag in (FLAG_UL, FLAG_OL):
                if current_flag is None:
                    current_flag = flag
                if flag == current_flag:
                    bullets.append(u"*" if flag == FLAG_UL else u"#")
                else:
                    break

        if flag != current_flag and buf[-1] == u" ":
            # this trick is to avoid a space when we switch
            # from (un)ordered to the other type on the same row
            # e.g. *# unorder + ordered item
            del buf[-1]

        buf.extend(bullets)

        buf.append(u" ")
        self.parseChildren(elt, buf)
        buf.append(u"\n")

    def parser_ol(self, elt, buf):
        self.parserList(elt, buf, FLAG_OL)

    def parser_p(self, elt, buf):
        self.parseChildren(elt, buf)
        buf.append(u"\n\n")

    def parser_pre(self, elt, buf):
        pre = u"".join(
            [
                child.toXml() if domish.IElement.providedBy(child) else unicode(child)
                for child in elt.children
            ]
        )
        pre = u" " + u"\n ".join(pre.split("\n"))
        buf.append(pre)

    def parser_q(self, elt, buf):
        quote_data = [unicode(elt)]

        lang = elt.getAttribute("lang")
        cite = elt.getAttribute("url")

        if lang:
            quote_data.append(lang)
        elif cite:
            quote_data.append(u"")

        if cite:
            quote_data.append(cite)

        buf.append(u"{{")
        buf.append(u"|".join(quote_data))
        buf.append(u"}}")

    def parser_span(self, elt, buf):
        self.parseChildren(elt, buf, block=True)

    def parser_strong(self, elt, buf):
        buf.append(u"__")
        self.parseChildren(elt, buf)
        buf.append(u"__")

    def parser_sup(self, elt, buf):
        # sup is mainly used for footnotes, so we check if we have an anchor inside
        children = list(
            [child for child in elt.children if unicode(child).strip() not in ("", "\n")]
        )
        if (
            len(children) == 1
            and domish.IElement.providedBy(children[0])
            and children[0].name == "a"
            and "#" in children[0].getAttribute("href", "")
        ):
            url = children[0]["href"]
            note_id = url[url.find("#") + 1 :]
            if not note_id:
                log.warning("bad link found in footnote")
                self.parserGeneric(elt, buf)
                return
            # this looks like a footnote
            buf.append(u"$$")
            buf.append(u" ")  # placeholder
            self.footnotes[note_id] = len(buf) - 1
            buf.append(u"$$")
        else:
            self.parserGeneric(elt, buf)

    def parser_ul(self, elt, buf):
        self.parserList(elt, buf, FLAG_UL)

    def parserList(self, elt, buf, type_):
        self.flags.append(type_)
        self.parseChildren(elt, buf, block=True)
        idx = 0
        for flag in reversed(self.flags):
            idx -= 1
            if flag == type_:
                del self.flags[idx]
                break

        if idx == 0:
            raise exceptions.InternalError(u"flag has been removed by an other parser")

    def parserHeading(self, elt, buf, level):
        buf.append((6 - level) * u"!")
        for child in elt.children:
            # we ignore other elements for a Hx title
            self.parserText(child, buf)
        buf.append(u"\n")

    def parserFootnote(self, elt, buf):
        for elt in elt.elements():
            # all children other than <p/> are ignored
            if elt.name == "p":
                a_elt = elt.a
                if a_elt is None:
                    log.warning(
                        u"<p/> element doesn't contain <a/> in footnote, ignoring it"
                    )
                    continue
                try:
                    note_idx = self.footnotes[a_elt["id"]]
                except KeyError:
                    log.warning(u"Note id doesn't match any known note, ignoring it")
                # we create a dummy element to parse all children after the <a/>
                dummy_elt = domish.Element((None, "note"))
                a_idx = elt.children.index(a_elt)
                dummy_elt.children = elt.children[a_idx + 1 :]
                note_buf = []
                self.parseChildren(dummy_elt, note_buf)
                # now we can replace the placeholder
                buf[note_idx] = u"".join(note_buf)

    def parserText(self, txt, buf, keep_whitespaces=False):
        txt = unicode(txt)
        if not keep_whitespaces:
            # we get text and only let one inter word space
            txt = u" ".join(txt.split())
        txt = re.sub(ESCAPE_CHARS, r"\\\1", txt)
        if txt:
            buf.append(txt)
        return txt

    def parserGeneric(self, elt, buf):
        # as dotclear wiki syntax handle arbitrary XHTML code
        # we use this feature to add elements that we don't know
        buf.append(u"\n\n///html\n{}\n///\n\n".format(elt.toXml()))

    def parseChildren(self, elt, buf, block=False):
        first_visible = True
        for child in elt.children:
            if not block and not first_visible and buf and buf[-1][-1] not in (" ", "\n"):
                # we add separation if it isn't already there
                buf.append(u" ")
            if domish.IElement.providedBy(child):
                self._parse(child, buf)
                first_visible = False
            else:
                appended = self.parserText(child, buf)
                if appended:
                    first_visible = False

    def _parse(self, elt, buf):
        elt_name = elt.name.lower()
        style = elt.getAttribute("style")
        if style and elt_name not in ELT_WITH_STYLE:
            # if we have style we use generic parser to put raw HTML
            # to avoid losing it
            parser = self.parserGeneric
        else:
            try:
                parser = getattr(self, "parser_{}".format(elt_name))
            except AttributeError:
                log.debug(
                    "Can't find parser for {} element, using generic one".format(elt.name)
                )
                parser = self.parserGeneric
        parser(elt, buf)

    def parse(self, elt):
        self.flags = []
        self.footnotes = {}
        buf = []
        self._parse(elt, buf)
        return u"".join(buf)

    def parseString(self, string):
        wrapped_html = u"<div>{}</div>".format(string)
        try:
            div_elt = xml_tools.ElementParser()(wrapped_html)
        except domish.ParserError as e:
            log.warning(u"Error while parsing HTML content: {}".format(e))
            return
        children = list(div_elt.elements())
        if len(children) == 1 and children[0].name == "div":
            div_elt = children[0]
        return self.parse(div_elt)


class DCWikiSyntax(object):
    SYNTAX_NAME = "wiki_dotclear"

    def __init__(self, host):
        log.info(_(u"Dotclear wiki syntax plugin initialization"))
        self.host = host
        self._dc_parser = DCWikiParser()
        self._xhtml_parser = XHTMLParser()
        self._stx = self.host.plugins["TEXT_SYNTAXES"]
        self._stx.addSyntax(
            self.SYNTAX_NAME, self.parseWiki, self.parseXHTML, [self._stx.OPT_NO_THREAD]
        )

    def parseWiki(self, wiki_stx):
        div_elt = self._dc_parser.parse(wiki_stx)
        return div_elt.toXml()

    def parseXHTML(self, xhtml):
        return self._xhtml_parser.parseString(xhtml)

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing various text syntaxes
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

import re
from cgi import escape
from functools import partial
from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

from twisted.internet import defer
from twisted.internet.threads import deferToThread
from sat.core import exceptions
from sat.tools import xml_tools

try:
    from lxml import html
    from lxml.html import clean
    from lxml import etree
except ImportError:
    raise exceptions.MissingModule(
        u"Missing module lxml, please download/install it from http://lxml.de/"
    )

log = getLogger(__name__)

CATEGORY = D_("Composition")
NAME = "Syntax"
_SYNTAX_XHTML = "xhtml"  # must be lower case
_SYNTAX_CURRENT = "@CURRENT@"

# TODO: check/adapt following list
# list initialy based on feedparser list (http://pythonhosted.org/feedparser/html-sanitization.html)
STYLES_WHITELIST = (
    "azimuth",
    "background-color",
    "border-bottom-color",
    "border-collapse",
    "border-color",
    "border-left-color",
    "border-right-color",
    "border-top-color",
    "clear",
    "color",
    "cursor",
    "direction",
    "display",
    "elevation",
    "float",
    "font",
    "font-family",
    "font-size",
    "font-style",
    "font-variant",
    "font-weight",
    "height",
    "letter-spacing",
    "line-height",
    "overflow",
    "pause",
    "pause-after",
    "pause-before",
    "pitch",
    "pitch-range",
    "richness",
    "speak",
    "speak-header",
    "speak-numeral",
    "speak-punctuation",
    "speech-rate",
    "stress",
    "text-align",
    "text-decoration",
    "text-indent",
    "unicode-bidi",
    "vertical-align",
    "voice-family",
    "volume",
    "white-space",
    "width",
)

# cf. https://www.w3.org/TR/html/syntax.html#void-elements
VOID_ELEMENTS = (
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "keygen",
    "link",
    "menuitem",
    "meta",
    "param",
    "source",
    "track",
    "wbr")

SAFE_ATTRS = html.defs.safe_attrs.union(("style", "poster", "controls"))
STYLES_VALUES_REGEX = (
    r"^("
    + "|".join(
        [
            "([a-z-]+)",  # alphabetical names
            "(#[0-9a-f]+)",  # hex value
            "(\d+(.\d+)? *(|%|em|ex|px|in|cm|mm|pt|pc))",  # values with units (or not)
            "rgb\( *((\d+(.\d+)?), *){2}(\d+(.\d+)?) *\)",  # rgb function
            "rgba\( *((\d+(.\d+)?), *){3}(\d+(.\d+)?) *\)",  # rgba function
        ]
    )
    + ") *(!important)?$"
)  # we accept "!important" at the end
STYLES_ACCEPTED_VALUE = re.compile(STYLES_VALUES_REGEX)

PLUGIN_INFO = {
    C.PI_NAME: "Text syntaxes",
    C.PI_IMPORT_NAME: "TEXT_SYNTAXES",
    C.PI_TYPE: "MISC",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "TextSyntaxes",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Management of various text syntaxes (XHTML-IM, Markdown, etc)"""
    ),
}


class TextSyntaxes(object):
    """ Text conversion class
    XHTML utf-8 is used as intermediate language for conversions
    """

    OPT_DEFAULT = "DEFAULT"
    OPT_HIDDEN = "HIDDEN"
    OPT_NO_THREAD = "NO_THREAD"
    SYNTAX_XHTML = _SYNTAX_XHTML
    SYNTAX_MARKDOWN = "markdown"
    SYNTAX_TEXT = "text"
    syntaxes = {}
    # default_syntax must be lower case
    default_syntax = SYNTAX_XHTML

    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param name="%(name)s" label="%(label)s" type="list" security="0">
            %(options)s
        </param>
    </category>
    </individual>
    </params>
    """

    params_data = {
        "category_name": CATEGORY,
        "category_label": _(CATEGORY),
        "name": NAME,
        "label": _(NAME),
        "syntaxes": syntaxes,
    }

    def __init__(self, host):
        log.info(_("Text syntaxes plugin initialization"))
        self.host = host
        self.addSyntax(
            self.SYNTAX_XHTML,
            lambda xhtml: defer.succeed(xhtml),
            lambda xhtml: defer.succeed(xhtml),
            TextSyntaxes.OPT_NO_THREAD,
        )
        # TODO: text => XHTML should add <a/> to url like in frontends
        #       it's probably best to move sat_frontends.tools.strings to sat.tools.common or similar
        self.addSyntax(
            self.SYNTAX_TEXT,
            lambda text: escape(text),
            lambda xhtml: self._removeMarkups(xhtml),
            [TextSyntaxes.OPT_HIDDEN],
        )
        try:
            import markdown, html2text
            from markdown.extensions import Extension

            # XXX: we disable raw HTML parsing by default, to avoid parsing error
            #      when the user is not aware of markdown and HTML
            class EscapeHTML(Extension):
                def extendMarkdown(self, md):
                    md.preprocessors.deregister('html_block')
                    md.inlinePatterns.deregister('html')

            def _html2text(html, baseurl=""):
                h = html2text.HTML2Text(baseurl=baseurl)
                h.body_width = 0  # do not truncate the lines, it breaks the long URLs
                return h.handle(html)

            self.addSyntax(
                self.SYNTAX_MARKDOWN,
                partial(markdown.markdown,
                        extensions=[
                            EscapeHTML(),
                            u'nl2br',
                            u'codehilite',
                            u'fenced_code',
                            u'sane_lists',
                            u'tables',
                            ],
                        extension_configs = {
                            u"codehilite": {
                                u"css_class": "highlight",
                            }
                        }),
                _html2text,
                [TextSyntaxes.OPT_DEFAULT],
            )
        except ImportError:
            log.warning(u"markdown or html2text not found, can't use Markdown syntax")
            log.info(
                u"You can download/install them from https://pythonhosted.org/Markdown/ and https://github.com/Alir3z4/html2text/"
            )
        host.bridge.addMethod(
            "syntaxConvert",
            ".plugin",
            in_sign="sssbs",
            out_sign="s",
            async=True,
            method=self.convert,
        )
        host.bridge.addMethod(
            "syntaxGet", ".plugin", in_sign="s", out_sign="s", method=self.getSyntax
        )
        if xml_tools.cleanXHTML is None:
            log.debug(u"Installing cleaning method")
            xml_tools.cleanXHTML = self.cleanXHTML

    def _updateParamOptions(self):
        data_synt = TextSyntaxes.syntaxes
        default_synt = TextSyntaxes.default_syntax
        syntaxes = []

        for syntax in data_synt.keys():
            flags = data_synt[syntax]["flags"]
            if TextSyntaxes.OPT_HIDDEN not in flags:
                syntaxes.append(syntax)

        syntaxes.sort(key=lambda synt: synt.lower())
        options = []

        for syntax in syntaxes:
            selected = 'selected="true"' if syntax == default_synt else ""
            options.append(u'<option value="%s" %s/>' % (syntax, selected))

        TextSyntaxes.params_data["options"] = u"\n".join(options)
        self.host.memory.updateParams(TextSyntaxes.params % TextSyntaxes.params_data)

    def getCurrentSyntax(self, profile):
        """ Return the selected syntax for the given profile

        @param profile: %(doc_profile)s
        @return: profile selected syntax
        """
        return self.host.memory.getParamA(NAME, CATEGORY, profile_key=profile)

    def _logError(self, failure, action=u"converting syntax"):
        log.error(
            u"Error while {action}: {failure}".format(action=action, failure=failure)
        )
        return failure

    def cleanStyle(self, styles):
        """"Clean unsafe CSS styles

        Remove styles not in the whitelist, or where the value doesn't match the regex
        @param styles_raw(unicode): CSS styles
        @return (unicode): cleaned styles
        """
        styles = styles.split(";")
        cleaned_styles = []
        for style in styles:
            try:
                key, value = style.split(":")
            except ValueError:
                continue
            key = key.lower().strip()
            if key not in STYLES_WHITELIST:
                continue
            value = value.lower().strip()
            if not STYLES_ACCEPTED_VALUE.match(value):
                continue
            if value == "none":
                continue
            cleaned_styles.append((key, value))
        return "; ".join(
            ["%s: %s" % (key_, value_) for key_, value_ in cleaned_styles]
        )

    def cleanXHTML(self, xhtml):
        """Clean XHTML text by removing potentially dangerous/malicious parts

        @param xhtml(unicode, lxml.etree._Element): raw HTML/XHTML text to clean
        @return (unicode): cleaned XHTML
        """

        if isinstance(xhtml, basestring):
            try:
                xhtml_elt = html.fromstring(xhtml)
            except etree.ParserError as e:
                if not xhtml.strip():
                    return u""
                log.error(u"Can't clean XHTML: {xhtml}".format(xhtml=xhtml))
                raise e
        elif isinstance(xhtml, html.HtmlElement):
            xhtml_elt = xhtml
        else:
            log.error("Only strings and HtmlElements can be cleaned")
            raise exceptions.DataError
        cleaner = clean.Cleaner(
            style=False, add_nofollow=False, safe_attrs=SAFE_ATTRS
        )
        xhtml_elt = cleaner.clean_html(xhtml_elt)
        for elt in xhtml_elt.xpath("//*[@style]"):
            elt.set("style", self.cleanStyle(elt.get("style")))
        # we remove self-closing elements for non-void elements
        for element in xhtml_elt.iter(tag=etree.Element):
            if not element.text:
                if element.tag in VOID_ELEMENTS:
                    element.text = None
                else:
                    element.text = u''
        return html.tostring(xhtml_elt, encoding=unicode, method="xml")

    def convert(
        self, text, syntax_from, syntax_to=_SYNTAX_XHTML, safe=True, profile=None
    ):
        """Convert a text between two syntaxes

        @param text: text to convert
        @param syntax_from: source syntax (e.g. "markdown")
        @param syntax_to: dest syntax (e.g.: "XHTML")
        @param safe: clean resulting XHTML to avoid malicious code if True
        @param profile: needed only when syntax_from or syntax_to is set to
            _SYNTAX_CURRENT
        @return(unicode): converted text
        """
        # FIXME: convert should be abled to handle domish.Element directly
        #        when dealing with XHTML
        # TODO: a way for parser to return parsing errors/warnings

        if syntax_from == _SYNTAX_CURRENT:
            syntax_from = self.getCurrentSyntax(profile)
        else:
            syntax_from = syntax_from.lower().strip()
        if syntax_to == _SYNTAX_CURRENT:
            syntax_to = self.getCurrentSyntax(profile)
        else:
            syntax_to = syntax_to.lower().strip()
        syntaxes = TextSyntaxes.syntaxes
        if syntax_from not in syntaxes:
            raise exceptions.NotFound(syntax_from)
        if syntax_to not in syntaxes:
            raise exceptions.NotFound(syntax_to)
        d = None

        if TextSyntaxes.OPT_NO_THREAD in syntaxes[syntax_from]["flags"]:
            d = defer.maybeDeferred(syntaxes[syntax_from]["to"], text)
        else:
            d = deferToThread(syntaxes[syntax_from]["to"], text)

        # TODO: keep only body element and change it to a div here ?

        if safe:
            d.addCallback(self.cleanXHTML)

        if TextSyntaxes.OPT_NO_THREAD in syntaxes[syntax_to]["flags"]:
            d.addCallback(syntaxes[syntax_to]["from"])
        else:
            d.addCallback(lambda xhtml: deferToThread(syntaxes[syntax_to]["from"], xhtml))

        # converters can add new lines that disturb the microblog change detection
        d.addCallback(lambda text: text.rstrip())
        return d

    def addSyntax(self, name, to_xhtml_cb, from_xhtml_cb, flags=None):
        """Add a new syntax to the manager

        @param name: unique name of the syntax
        @param to_xhtml_cb: callback to convert from syntax to XHTML
        @param from_xhtml_cb: callback to convert from XHTML to syntax
        @param flags: set of optional flags, can be:
            TextSyntaxes.OPT_DEFAULT: use as the default syntax (replace former one)
            TextSyntaxes.OPT_HIDDEN: do not show in parameters
            TextSyntaxes.OPT_NO_THREAD: do not defer to thread when converting (the callback may then return a deferred)
        """
        flags = flags if flags is not None else []
        if TextSyntaxes.OPT_HIDDEN in flags and TextSyntaxes.OPT_DEFAULT in flags:
            raise ValueError(
                u"{} and {} are mutually exclusive".format(
                    TextSyntaxes.OPT_HIDDEN, TextSyntaxes.OPT_DEFAULT
                )
            )

        syntaxes = TextSyntaxes.syntaxes
        key = name.lower().strip()
        if key in syntaxes:
            raise exceptions.ConflictError(
                u"This syntax key already exists: {}".format(key)
            )
        syntaxes[key] = {
            "name": name,
            "to": to_xhtml_cb,
            "from": from_xhtml_cb,
            "flags": flags,
        }
        if TextSyntaxes.OPT_DEFAULT in flags:
            TextSyntaxes.default_syntax = key

        self._updateParamOptions()

    def getSyntax(self, name):
        """get syntax key corresponding to a name

        @raise exceptions.NotFound: syntax doesn't exist
        """
        key = name.lower().strip()
        if key in self.syntaxes:
            return key
        raise exceptions.NotFound

    def _removeMarkups(self, xhtml):
        """Remove XHTML markups from the given string.

        @param xhtml: the XHTML string to be cleaned
        @return: the cleaned string
        """
        cleaner = clean.Cleaner(kill_tags=["style"])
        cleaned = cleaner.clean_html(html.fromstring(xhtml))
        return html.tostring(cleaned, encoding=unicode, method="text")

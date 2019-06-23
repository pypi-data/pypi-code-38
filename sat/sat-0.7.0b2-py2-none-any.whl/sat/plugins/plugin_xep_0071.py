#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Publish-Subscribe (xep-0071)
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools.common import data_format

from twisted.internet import defer
from wokkel import disco, iwokkel
from zope.interface import implements

# from lxml import etree
try:
    from lxml import html
except ImportError:
    raise exceptions.MissingModule(
        u"Missing module lxml, please download/install it from http://lxml.de/"
    )
try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

NS_XHTML_IM = "http://jabber.org/protocol/xhtml-im"
NS_XHTML = "http://www.w3.org/1999/xhtml"

PLUGIN_INFO = {
    C.PI_NAME: "XHTML-IM Plugin",
    C.PI_IMPORT_NAME: "XEP-0071",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0071"],
    C.PI_DEPENDENCIES: ["TEXT_SYNTAXES"],
    C.PI_MAIN: "XEP_0071",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of XHTML-IM"""),
}

allowed = {
    "a": set(["href", "style", "type"]),
    "blockquote": set(["style"]),
    "body": set(["style"]),
    "br": set([]),
    "cite": set(["style"]),
    "em": set([]),
    "img": set(["alt", "height", "src", "style", "width"]),
    "li": set(["style"]),
    "ol": set(["style"]),
    "p": set(["style"]),
    "span": set(["style"]),
    "strong": set([]),
    "ul": set(["style"]),
}

styles_allowed = [
    "background-color",
    "color",
    "font-family",
    "font-size",
    "font-style",
    "font-weight",
    "margin-left",
    "margin-right",
    "text-align",
    "text-decoration",
]

blacklist = ["script"]  # tag that we have to kill (we don't keep content)


class XEP_0071(object):
    SYNTAX_XHTML_IM = "XHTML-IM"

    def __init__(self, host):
        log.info(_("XHTML-IM plugin initialization"))
        self.host = host
        self._s = self.host.plugins["TEXT_SYNTAXES"]
        self._s.addSyntax(
            self.SYNTAX_XHTML_IM,
            lambda xhtml: xhtml,
            self.XHTML2XHTML_IM,
            [self._s.OPT_HIDDEN],
        )
        host.trigger.add("MessageReceived", self.messageReceivedTrigger)
        host.trigger.add("sendMessage", self.sendMessageTrigger)

    def getHandler(self, client):
        return XEP_0071_handler(self)

    def _messagePostTreat(self, data, message_elt, body_elts, client):
        """Callback which manage the post treatment of the message in case of XHTML-IM found

        @param data: data send by MessageReceived trigger through post_treat deferred
        @param message_elt: whole <message> stanza
        @param body_elts: XHTML-IM body elements found
        @return: the data with the extra parameter updated
        """
        # TODO: check if text only body is empty, then try to convert XHTML-IM to pure text and show a warning message
        def converted(xhtml, lang):
            if lang:
                data["extra"]["xhtml_{}".format(lang)] = xhtml
            else:
                data["extra"]["xhtml"] = xhtml

        defers = []
        for body_elt in body_elts:
            lang = body_elt.getAttribute((C.NS_XML, "lang"), "")
            treat_d = defer.succeed(None)  #  deferred used for treatments
            if self.host.trigger.point(
                "xhtml_post_treat", client, message_elt, body_elt, lang, treat_d
            ):
                continue
            treat_d.addCallback(
                lambda __: self._s.convert(
                    body_elt.toXml(), self.SYNTAX_XHTML_IM, safe=True
                )
            )
            treat_d.addCallback(converted, lang)
            defers.append(treat_d)

        d_list = defer.DeferredList(defers)
        d_list.addCallback(lambda __: data)
        return d_list

    def _fill_body_text(self, text, data, lang):
        data["message"][lang or ""] = text
        message_elt = data["xml"]
        body_elt = message_elt.addElement("body", content=text)
        if lang:
            body_elt[(C.NS_XML, "lang")] = lang

    def _check_body_text(self, data, lang, markup, syntax, defers):
        """check if simple text message exists, and fill if needed"""
        if not (lang or "") in data["message"]:
            d = self._s.convert(markup, syntax, self._s.SYNTAX_TEXT)
            d.addCallback(self._fill_body_text, data, lang)
            defers.append(d)

    def _sendMessageAddRich(self, data, client):
        """ Construct XHTML-IM node and add it XML element

        @param data: message data as sended by sendMessage callback
        """
        # at this point, either ['extra']['rich'] or ['extra']['xhtml'] exists
        # but both can't exist at the same time
        message_elt = data["xml"]
        html_elt = message_elt.addElement((NS_XHTML_IM, "html"))

        def syntax_converted(xhtml_im, lang):
            body_elt = html_elt.addElement((NS_XHTML, "body"))
            if lang:
                body_elt[(C.NS_XML, "lang")] = lang
                data["extra"]["xhtml_{}".format(lang)] = xhtml_im
            else:
                data["extra"]["xhtml"] = xhtml_im
            body_elt.addRawXml(xhtml_im)

        syntax = self._s.getCurrentSyntax(client.profile)
        defers = []
        if u"xhtml" in data["extra"]:
            # we have directly XHTML
            for lang, xhtml in data_format.getSubDict("xhtml", data["extra"]):
                self._check_body_text(data, lang, xhtml, self._s.SYNTAX_XHTML, defers)
                d = self._s.convert(xhtml, self._s.SYNTAX_XHTML, self.SYNTAX_XHTML_IM)
                d.addCallback(syntax_converted, lang)
                defers.append(d)
        elif u"rich" in data["extra"]:
            # we have rich syntax to convert
            for lang, rich_data in data_format.getSubDict("rich", data["extra"]):
                self._check_body_text(data, lang, rich_data, syntax, defers)
                d = self._s.convert(rich_data, syntax, self.SYNTAX_XHTML_IM)
                d.addCallback(syntax_converted, lang)
                defers.append(d)
        else:
            exceptions.InternalError(u"xhtml or rich should be present at this point")
        d_list = defer.DeferredList(defers)
        d_list.addCallback(lambda __: data)
        return d_list

    def messageReceivedTrigger(self, client, message, post_treat):
        """ Check presence of XHTML-IM in message
        """
        try:
            html_elt = message.elements(NS_XHTML_IM, "html").next()
        except StopIteration:
            # No XHTML-IM
            pass
        else:
            body_elts = html_elt.elements(NS_XHTML, "body")
            post_treat.addCallback(self._messagePostTreat, message, body_elts, client)
        return True

    def sendMessageTrigger(self, client, data, pre_xml_treatments, post_xml_treatments):
        """ Check presence of rich text in extra """
        rich = {}
        xhtml = {}
        for key, value in data["extra"].iteritems():
            if key.startswith("rich"):
                rich[key[5:]] = value
            elif key.startswith("xhtml"):
                xhtml[key[6:]] = value
        if rich and xhtml:
            raise exceptions.DataError(
                _(u"Can't have XHTML and rich content at the same time")
            )
        if rich or xhtml:
            if rich:
                data["rich"] = rich
            else:
                data["xhtml"] = xhtml
            post_xml_treatments.addCallback(self._sendMessageAddRich, client)
        return True

    def _purgeStyle(self, styles_raw):
        """ Remove unauthorised styles according to the XEP-0071
        @param styles_raw: raw styles (value of the style attribute)
        """
        purged = []

        styles = [style.strip().split(":") for style in styles_raw.split(";")]

        for style_tuple in styles:
            if len(style_tuple) != 2:
                continue
            name, value = style_tuple
            name = name.strip()
            if name not in styles_allowed:
                continue
            purged.append((name, value.strip()))

        return u"; ".join([u"%s: %s" % data for data in purged])

    def XHTML2XHTML_IM(self, xhtml):
        """ Convert XHTML document to XHTML_IM subset
        @param xhtml: raw xhtml to convert
        """
        # TODO: more clever tag replacement (replace forbidden tags with equivalents when possible)

        parser = html.HTMLParser(remove_comments=True, encoding="utf-8")
        root = html.fromstring(xhtml, parser=parser)
        body_elt = root.find("body")
        if body_elt is None:
            # we use the whole XML as body if no body element is found
            body_elt = html.Element("body")
            body_elt.append(root)
        else:
            body_elt.attrib.clear()

        allowed_tags = allowed.keys()
        to_strip = []
        for elem in body_elt.iter():
            if elem.tag not in allowed_tags:
                to_strip.append(elem)
            else:
                # we remove unallowed attributes
                attrib = elem.attrib
                att_to_remove = set(attrib).difference(allowed[elem.tag])
                for att in att_to_remove:
                    del (attrib[att])
                if "style" in attrib:
                    attrib["style"] = self._purgeStyle(attrib["style"])

        for elem in to_strip:
            if elem.tag in blacklist:
                # we need to remove the element and all descendants
                log.debug(u"removing black listed tag: %s" % (elem.tag))
                elem.drop_tree()
            else:
                elem.drop_tag()
        if len(body_elt) != 1:
            root_elt = body_elt
            body_elt.tag = "p"
        else:
            root_elt = body_elt[0]

        return html.tostring(root_elt, encoding="unicode", method="xml")


class XEP_0071_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_XHTML_IM)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

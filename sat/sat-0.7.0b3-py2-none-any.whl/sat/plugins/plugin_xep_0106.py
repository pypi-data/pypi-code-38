#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Explicit Message Encryption
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
from sat.core.log import getLogger
from twisted.words.protocols.jabber import xmlstream
from zope.interface import implements
from wokkel import disco

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: u"JID Escaping",
    C.PI_IMPORT_NAME: u"XEP-0106",
    C.PI_TYPE: u"XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: [u"XEP-0106"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: u"XEP_0106",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: _(u"""(Un)escape JID to use disallowed chars in local parts"""),
}

NS_JID_ESCAPING = ur"jid\20escaping"
ESCAPE_MAP = {
    ' ': r'\20',
    '"': r'\22',
    '&': r'\26',
    "'": r'\27',
    '/': r'\2f',
    ':': r'\3a',
    '<': r'\3c',
    '>': r'\3e',
    '@': r'\40',
    '\\': r'\5c',
}


class XEP_0106(object):

    def __init__(self, host):
        self.reverse_map = {v:k for k,v in ESCAPE_MAP.iteritems()}

    def getHandler(self, client):
        return XEP_0106_handler()

    def escape(self, text):
        """Escape text

        @param text(unicode): text to escape
        @return (unicode): escaped text
        @raise ValueError: text can't be escaped
        """
        if not text or text[0] == ' ' or text[-1] == ' ':
            raise ValueError(u"text must not be empty, or start or end with a whitespace")
        escaped = []
        for c in text:
            if c in ESCAPE_MAP:
                escaped.append(ESCAPE_MAP[c])
            else:
                escaped.append(c)
        return u''.join(escaped)

    def unescape(self, escaped):
        """Unescape text

        @param escaped(unicode): text to unescape
        @return (unicode): unescaped text
        @raise ValueError: text can't be unescaped
        """
        if not escaped or escaped.startswith(r'\27') or escaped.endswith(r'\27'):
            raise ValueError(u"escaped value must not be empty, or start or end with a "
                             u"whitespace")
        unescaped = []
        idx = 0
        while idx < len(escaped):
            char_seq = escaped[idx:idx+3]
            if char_seq in self.reverse_map:
                unescaped.append(self.reverse_map[char_seq])
                idx += 3
            else:
                unescaped.append(escaped[idx])
                idx += 1
        return u''.join(unescaped)


class XEP_0106_handler(xmlstream.XMPPHandler):
    implements(disco.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_JID_ESCAPING)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

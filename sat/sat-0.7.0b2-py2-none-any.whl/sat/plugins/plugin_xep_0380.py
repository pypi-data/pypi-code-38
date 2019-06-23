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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger
from twisted.words.protocols.jabber import jid

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: u"Explicit Message Encryption",
    C.PI_IMPORT_NAME: u"XEP-0380",
    C.PI_TYPE: u"SEC",
    C.PI_PROTOCOLS: [u"XEP-0380"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: u"XEP_0380",
    C.PI_HANDLER: u"no",
    C.PI_DESCRIPTION: _(u"""Implementation of Explicit Message Encryption"""),
}

NS_EME = u"urn:xmpp:eme:0"
KNOWN_NAMESPACES = {
    u"urn:xmpp:otr:0": u"OTR",
    u"jabber:x:encrypted": u"Legacy OpenPGP",
    u"urn:xmpp:openpgp:0": u"OpenPGP for XMPP",
}


class XEP_0380(object):

    def __init__(self, host):
        self.host = host
        host.trigger.add("sendMessage", self._sendMessageTrigger)
        host.trigger.add("MessageReceived", self._MessageReceivedTrigger, priority=100)
        host.registerNamespace(u"eme", NS_EME)

    def _addEMEElement(self, mess_data, namespace, name):
        message_elt = mess_data[u'xml']
        encryption_elt = message_elt.addElement((NS_EME, u'encryption'))
        encryption_elt[u'namespace'] = namespace
        if name is not None:
            encryption_elt[u'name'] = name
        return mess_data

    def _sendMessageTrigger(self, client, mess_data, __, post_xml_treatments):
        encryption = mess_data.get(C.MESS_KEY_ENCRYPTION)
        if encryption is not None:
            namespace = encryption['plugin'].namespace
            if namespace not in KNOWN_NAMESPACES:
                name = encryption[u'plugin'].name
            else:
                name = None
            post_xml_treatments.addCallback(
                self._addEMEElement, namespace=namespace, name=name)
        return True

    def _MessageReceivedTrigger(self, client, message_elt, post_treat):
        try:
            encryption_elt = next(message_elt.elements(NS_EME, u'encryption'))
        except StopIteration:
            return True

        namespace = encryption_elt['namespace']
        if namespace in client.encryption.getNamespaces():
            # message is encrypted and we can decrypt it
            return True

        name = KNOWN_NAMESPACES.get(namespace, encryption_elt.getAttribute(u"name"))

        # at this point, message is encrypted but we know that we can't decrypt it,
        # we need to notify the user
        sender_s = message_elt[u'from']
        to_jid = jid.JID(message_elt[u'from'])
        algorithm = u"{} [{}]".format(name, namespace) if name else namespace
        log.warning(
            _(u"Message from {sender} is encrypted with {algorithm} and we can't "
              u"decrypt it.".format(sender=message_elt['from'], algorithm=algorithm)))

        user_msg = D_(
            u"User {sender} sent you an encrypted message (encrypted with {algorithm}), "
            u"and we can't decrypt it.").format(sender=sender_s, algorithm=algorithm)

        extra = {C.MESS_EXTRA_INFO: C.EXTRA_INFO_DECR_ERR}
        client.feedback(to_jid, user_msg, extra)
        return False

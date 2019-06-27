#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing gateways (xep-0047)
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
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.constants import Const as C
from sat.core import exceptions
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber import error
from twisted.internet import reactor
from twisted.internet import defer
from twisted.python import failure

from wokkel import disco, iwokkel

from zope.interface import implements

import base64

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

MESSAGE = "/message"
IQ_SET = '/iq[@type="set"]'
NS_IBB = "http://jabber.org/protocol/ibb"
IBB_OPEN = IQ_SET + '/open[@xmlns="' + NS_IBB + '"]'
IBB_CLOSE = IQ_SET + '/close[@xmlns="' + NS_IBB + '" and @sid="{}"]'
IBB_IQ_DATA = IQ_SET + '/data[@xmlns="' + NS_IBB + '" and @sid="{}"]'
IBB_MESSAGE_DATA = MESSAGE + '/data[@xmlns="' + NS_IBB + '" and @sid="{}"]'
TIMEOUT = 120  # timeout for workflow
DEFER_KEY = "finished"  # key of the deferred used to track session end

PLUGIN_INFO = {
    C.PI_NAME: "In-Band Bytestream Plugin",
    C.PI_IMPORT_NAME: "XEP-0047",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0047"],
    C.PI_MAIN: "XEP_0047",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of In-Band Bytestreams"""),
}


class XEP_0047(object):
    NAMESPACE = NS_IBB
    BLOCK_SIZE = 4096

    def __init__(self, host):
        log.info(_("In-Band Bytestreams plugin initialization"))
        self.host = host

    def getHandler(self, client):
        return XEP_0047_handler(self)

    def profileConnected(self, client):
        client.xep_0047_current_stream = {}  # key: stream_id, value: data(dict)

    def _timeOut(self, sid, client):
        """Delete current_stream id, called after timeout

        @param sid(unicode): session id of client.xep_0047_current_stream
        @param client: %(doc_client)s
        """
        log.info(
            u"In-Band Bytestream: TimeOut reached for id {sid} [{profile}]".format(
                sid=sid, profile=client.profile
            )
        )
        self._killSession(sid, client, "TIMEOUT")

    def _killSession(self, sid, client, failure_reason=None):
        """Delete a current_stream id, clean up associated observers

        @param sid(unicode): session id
        @param client: %(doc_client)s
        @param failure_reason(None, unicode): if None the session is successful
            else, will be used to call failure_cb
        """
        try:
            session = client.xep_0047_current_stream[sid]
        except KeyError:
            log.warning(u"kill id called on a non existant id")
            return

        try:
            observer_cb = session["observer_cb"]
        except KeyError:
            pass
        else:
            client.xmlstream.removeObserver(session["event_data"], observer_cb)

        if session["timer"].active():
            session["timer"].cancel()

        del client.xep_0047_current_stream[sid]

        success = failure_reason is None
        stream_d = session[DEFER_KEY]

        if success:
            stream_d.callback(None)
        else:
            stream_d.errback(failure.Failure(exceptions.DataError(failure_reason)))

    def createSession(self, *args, **kwargs):
        """like [_createSession] but return the session deferred instead of the whole session

        session deferred is fired when transfer is finished
        """
        return self._createSession(*args, **kwargs)[DEFER_KEY]

    def _createSession(self, client, stream_object, local_jid, to_jid, sid):
        """Called when a bytestream is imminent

        @param stream_object(IConsumer): stream object where data will be written
        @param local_jid(jid.JID): same as [startStream]
        @param to_jid(jid.JId): jid of the other peer
        @param sid(unicode): session id
        @return (dict): session data
        """
        if sid in client.xep_0047_current_stream:
            raise exceptions.ConflictError(u"A session with this id already exists !")
        session_data = client.xep_0047_current_stream[sid] = {
            "id": sid,
            DEFER_KEY: defer.Deferred(),
            "local_jid": local_jid,
            "to": to_jid,
            "stream_object": stream_object,
            "seq": -1,
            "timer": reactor.callLater(TIMEOUT, self._timeOut, sid, client),
        }

        return session_data

    def _onIBBOpen(self, iq_elt, client):
        """"Called when an IBB <open> element is received

        @param iq_elt(domish.Element): the whole <iq> stanza
        """
        log.debug(_(u"IBB stream opening"))
        iq_elt.handled = True
        open_elt = iq_elt.elements(NS_IBB, "open").next()
        block_size = open_elt.getAttribute("block-size")
        sid = open_elt.getAttribute("sid")
        stanza = open_elt.getAttribute("stanza", "iq")
        if not sid or not block_size or int(block_size) > 65535:
            return self._sendError("not-acceptable", sid or None, iq_elt, client)
        if not sid in client.xep_0047_current_stream:
            log.warning(_(u"Ignoring unexpected IBB transfer: %s" % sid))
            return self._sendError("not-acceptable", sid or None, iq_elt, client)
        session_data = client.xep_0047_current_stream[sid]
        if session_data["to"] != jid.JID(iq_elt["from"]):
            log.warning(
                _("sended jid inconsistency (man in the middle attack attempt ?)")
            )
            return self._sendError("not-acceptable", sid, iq_elt, client)

        # at this stage, the session looks ok and will be accepted

        # we reset the timeout:
        session_data["timer"].reset(TIMEOUT)

        # we save the xmlstream, events and observer data to allow observer removal
        session_data["event_data"] = event_data = (
            IBB_MESSAGE_DATA if stanza == "message" else IBB_IQ_DATA
        ).format(sid)
        session_data["observer_cb"] = observer_cb = self._onIBBData
        event_close = IBB_CLOSE.format(sid)
        # we now set the stream observer to look after data packet
        # FIXME: if we never get the events, the observers stay.
        #        would be better to have generic observer and check id once triggered
        client.xmlstream.addObserver(event_data, observer_cb, client=client)
        client.xmlstream.addOnetimeObserver(event_close, self._onIBBClose, client=client)
        # finally, we send the accept stanza
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        client.send(iq_result_elt)

    def _onIBBClose(self, iq_elt, client):
        """"Called when an IBB <close> element is received

        @param iq_elt(domish.Element): the whole <iq> stanza
        """
        iq_elt.handled = True
        log.debug(_("IBB stream closing"))
        close_elt = iq_elt.elements(NS_IBB, "close").next()
        # XXX: this observer is only triggered on valid sid, so we don't need to check it
        sid = close_elt["sid"]

        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        client.send(iq_result_elt)
        self._killSession(sid, client)

    def _onIBBData(self, element, client):
        """Observer called on <iq> or <message> stanzas with data element

        Manage the data elelement (check validity and write to the stream_object)
        @param element(domish.Element): <iq> or <message> stanza
        """
        element.handled = True
        data_elt = element.elements(NS_IBB, "data").next()
        sid = data_elt["sid"]

        try:
            session_data = client.xep_0047_current_stream[sid]
        except KeyError:
            log.warning(_(u"Received data for an unknown session id"))
            return self._sendError("item-not-found", None, element, client)

        from_jid = session_data["to"]
        stream_object = session_data["stream_object"]

        if from_jid.full() != element["from"]:
            log.warning(
                _(
                    u"sended jid inconsistency (man in the middle attack attempt ?)\ninitial={initial}\ngiven={given}"
                ).format(initial=from_jid, given=element["from"])
            )
            if element.name == "iq":
                self._sendError("not-acceptable", sid, element, client)
            return

        session_data["seq"] = (session_data["seq"] + 1) % 65535
        if int(data_elt.getAttribute("seq", -1)) != session_data["seq"]:
            log.warning(_(u"Sequence error"))
            if element.name == "iq":
                reason = "not-acceptable"
                self._sendError(reason, sid, element, client)
            self.terminateStream(session_data, client, reason)
            return

        # we reset the timeout:
        session_data["timer"].reset(TIMEOUT)

        # we can now decode the data
        try:
            stream_object.write(base64.b64decode(str(data_elt)))
        except TypeError:
            # The base64 data is invalid
            log.warning(_(u"Invalid base64 data"))
            if element.name == "iq":
                self._sendError("not-acceptable", sid, element, client)
            self.terminateStream(session_data, client, reason)
            return

        # we can now ack success
        if element.name == "iq":
            iq_result_elt = xmlstream.toResponse(element, "result")
            client.send(iq_result_elt)

    def _sendError(self, error_condition, sid, iq_elt, client):
        """Send error stanza

        @param error_condition: one of twisted.words.protocols.jabber.error.STANZA_CONDITIONS keys
        @param sid(unicode,None): jingle session id, or None, if session must not be destroyed
        @param iq_elt(domish.Element): full <iq> stanza
        @param client: %(doc_client)s
        """
        iq_elt = error.StanzaError(error_condition).toResponse(iq_elt)
        log.warning(
            u"Error while managing in-band bytestream session, cancelling: {}".format(
                error_condition
            )
        )
        if sid is not None:
            self._killSession(sid, client, error_condition)
        client.send(iq_elt)

    def startStream(self, client, stream_object, local_jid, to_jid, sid, block_size=None):
        """Launch the stream workflow

        @param stream_object(ifaces.IStreamProducer): stream object to send
        @param local_jid(jid.JID): jid to use as local jid
            This is needed for client which can be addressed with a different jid than
            client.jid if a local part is used (e.g. piotr@file.example.net where
            client.jid would be file.example.net)
        @param to_jid(jid.JID): JID of the recipient
        @param sid(unicode): Stream session id
        @param block_size(int, None): size of the block (or None for default)
        """
        session_data = self._createSession(client, stream_object, local_jid, to_jid, sid)

        if block_size is None:
            block_size = XEP_0047.BLOCK_SIZE
        assert block_size <= 65535
        session_data["block_size"] = block_size

        iq_elt = client.IQ()
        iq_elt["from"] = local_jid.full()
        iq_elt["to"] = to_jid.full()
        open_elt = iq_elt.addElement((NS_IBB, "open"))
        open_elt["block-size"] = str(block_size)
        open_elt["sid"] = sid
        open_elt["stanza"] = "iq"  # TODO: manage <message> stanza ?
        args = [session_data, client]
        d = iq_elt.send()
        d.addCallbacks(self._IQDataStreamCb, self._IQDataStreamEb, args, None, args)
        return session_data[DEFER_KEY]

    def _IQDataStreamCb(self, iq_elt, session_data, client):
        """Called during the whole data streaming

        @param iq_elt(domish.Element): iq result
        @param session_data(dict): data of this streaming session
        @param client: %(doc_client)s
        """
        session_data["timer"].reset(TIMEOUT)

        buffer_ = session_data["stream_object"].read(session_data["block_size"])
        if buffer_:
            next_iq_elt = client.IQ()
            next_iq_elt["from"] = session_data["local_jid"].full()
            next_iq_elt["to"] = session_data["to"].full()
            data_elt = next_iq_elt.addElement((NS_IBB, "data"))
            seq = session_data["seq"] = (session_data["seq"] + 1) % 65535
            data_elt["seq"] = unicode(seq)
            data_elt["sid"] = session_data["id"]
            data_elt.addContent(base64.b64encode(buffer_))
            args = [session_data, client]
            d = next_iq_elt.send()
            d.addCallbacks(self._IQDataStreamCb, self._IQDataStreamEb, args, None, args)
        else:
            self.terminateStream(session_data, client)

    def _IQDataStreamEb(self, failure, session_data, client):
        if failure.check(error.StanzaError):
            log.warning(u"IBB transfer failed: {}".format(failure.value))
        else:
            log.error(u"IBB transfer failed: {}".format(failure.value))
        self.terminateStream(session_data, client, "IQ_ERROR")

    def terminateStream(self, session_data, client, failure_reason=None):
        """Terminate the stream session

        @param session_data(dict): data of this streaming session
        @param client: %(doc_client)s
        @param failure_reason(unicode, None): reason of the failure, or None if steam was successful
        """
        iq_elt = client.IQ()
        iq_elt["from"] = session_data["local_jid"].full()
        iq_elt["to"] = session_data["to"].full()
        close_elt = iq_elt.addElement((NS_IBB, "close"))
        close_elt["sid"] = session_data["id"]
        iq_elt.send()
        self._killSession(session_data["id"], client, failure_reason)


class XEP_0047_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, parent):
        self.plugin_parent = parent

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            IBB_OPEN, self.plugin_parent._onIBBOpen, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_IBB)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing pipes (experimental)
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
from sat.core import exceptions
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools import xml_tools
from sat.tools import stream
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import endpoints
from twisted.internet import reactor
from twisted.internet import error
from twisted.internet import interfaces
from zope import interface
import errno

NS_STREAM = "http://salut-a-toi.org/protocol/stream"
SECURITY_LIMIT = 30
START_PORT = 8888

PLUGIN_INFO = {
    C.PI_NAME: "Jingle Stream Plugin",
    C.PI_IMPORT_NAME: "STREAM",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0166"],
    C.PI_MAIN: "JingleStream",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Jingle Stream plugin"""),
}

CONFIRM = D_(u"{peer} wants to send you a stream, do you accept ?")
CONFIRM_TITLE = D_(u"Stream Request")


class StreamProtocol(protocol.Protocol):
    def __init__(self):
        self.pause = False

    def setPause(self, paused):
        # in Python 2.x, Twisted classes are old style
        # so we can use property and setter
        if paused:
            if not self.pause:
                self.transport.pauseProducing()
                self.pause = True
        else:
            if self.pause:
                self.transport.resumeProducing()
                self.pause = False

    def disconnect(self):
        self.transport.loseConnection()

    def connectionMade(self):
        if self.factory.client_conn is not None:
            self.transport.loseConnection()
        self.factory.setClientConn(self)

    def dataReceived(self, data):
        self.factory.writeToConsumer(data)

    def sendData(self, data):
        self.transport.write(data)

    def connectionLost(self, reason):
        if self.factory.client_conn != self:
            # only the first connected client_conn is relevant
            return

        if reason.type == error.ConnectionDone:
            self.factory.streamFinished()
        else:
            self.factory.streamFailed(reason)


@interface.implementer(stream.IStreamProducer)
@interface.implementer(interfaces.IPushProducer)
@interface.implementer(interfaces.IConsumer)
class StreamFactory(protocol.Factory):
    protocol = StreamProtocol
    consumer = None
    producer = None
    deferred = None

    def __init__(self):
        self.client_conn = None

    def setClientConn(self, stream_protocol):
        # in Python 2.x, Twisted classes are old style
        # so we can use property and setter
        assert self.client_conn is None
        self.client_conn = stream_protocol
        if self.consumer is None:
            self.client_conn.setPause(True)

    def startStream(self, consumer):
        if self.consumer is not None:
            raise exceptions.InternalError(
                _(u"stream can't be used with multiple consumers")
            )
        assert self.deferred is None
        self.consumer = consumer
        consumer.registerProducer(self, True)
        self.deferred = defer.Deferred()
        if self.client_conn is not None:
            self.client_conn.setPause(False)
        return self.deferred

    def streamFinished(self):
        self.client_conn = None
        if self.consumer:
            self.consumer.unregisterProducer()
            self.port_listening.stopListening()
        self.deferred.callback(None)

    def streamFailed(self, failure_):
        self.client_conn = None
        if self.consumer:
            self.consumer.unregisterProducer()
            self.port_listening.stopListening()
            self.deferred.errback(failure_)
        elif self.producer:
            self.producer.stopProducing()

    def stopStream(self):
        if self.client_conn is not None:
            self.client_conn.disconnect()

    def registerProducer(self, producer, streaming):
        self.producer = producer

    def pauseProducing(self):
        self.client_conn.setPause(True)

    def resumeProducing(self):
        self.client_conn.setPause(False)

    def stopProducing(self):
        if self.client_conn:
            self.client_conn.disconnect()

    def write(self, data):
        try:
            self.client_conn.sendData(data)
        except AttributeError:
            log.warning(_(u"No client connected, can't send data"))

    def writeToConsumer(self, data):
        self.consumer.write(data)


class JingleStream(object):
    """This non standard jingle application send byte stream"""

    def __init__(self, host):
        log.info(_("Plugin Stream initialization"))
        self.host = host
        self._j = host.plugins["XEP-0166"]  # shortcut to access jingle
        self._j.registerApplication(NS_STREAM, self)
        host.bridge.addMethod(
            "streamOut",
            ".plugin",
            in_sign="ss",
            out_sign="s",
            method=self._streamOut,
            async=True,
        )

    # jingle callbacks

    def _streamOut(self, to_jid_s, profile_key):
        client = self.host.getClient(profile_key)
        return self.streamOut(client, jid.JID(to_jid_s))

    @defer.inlineCallbacks
    def streamOut(self, client, to_jid):
        """send a stream

        @param peer_jid(jid.JID): recipient
        @return: an unique id to identify the transfer
        """
        port = START_PORT
        factory = StreamFactory()
        while True:
            endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
            try:
                port_listening = yield endpoint.listen(factory)
            except error.CannotListenError as e:
                if e.socketError.errno == errno.EADDRINUSE:
                    port += 1
                else:
                    raise e
            else:
                factory.port_listening = port_listening
                break
        self._j.initiate(
            client,
            to_jid,
            [
                {
                    "app_ns": NS_STREAM,
                    "senders": self._j.ROLE_INITIATOR,
                    "app_kwargs": {"stream_object": factory},
                }
            ],
        )
        defer.returnValue(unicode(port))

    def jingleSessionInit(self, client, session, content_name, stream_object):
        content_data = session["contents"][content_name]
        application_data = content_data["application_data"]
        assert "stream_object" not in application_data
        application_data["stream_object"] = stream_object
        desc_elt = domish.Element((NS_STREAM, "description"))
        return desc_elt

    @defer.inlineCallbacks
    def jingleRequestConfirmation(self, client, action, session, content_name, desc_elt):
        """This method request confirmation for a jingle session"""
        content_data = session["contents"][content_name]
        if content_data["senders"] not in (
            self._j.ROLE_INITIATOR,
            self._j.ROLE_RESPONDER,
        ):
            log.warning(u"Bad sender, assuming initiator")
            content_data["senders"] = self._j.ROLE_INITIATOR

        confirm_data = yield xml_tools.deferDialog(
            self.host,
            _(CONFIRM).format(peer=session["peer_jid"].full()),
            _(CONFIRM_TITLE),
            type_=C.XMLUI_DIALOG_CONFIRM,
            action_extra={
                "meta_from_jid": session["peer_jid"].full(),
                "meta_type": "STREAM",
            },
            security_limit=SECURITY_LIMIT,
            profile=client.profile,
        )

        if not C.bool(confirm_data["answer"]):
            defer.returnValue(False)
        try:
            port = int(confirm_data["port"])
        except (ValueError, KeyError):
            raise exceptions.DataError(_(u"given port is invalid"))
        endpoint = endpoints.TCP4ClientEndpoint(reactor, "localhost", port)
        factory = StreamFactory()
        yield endpoint.connect(factory)
        content_data["stream_object"] = factory
        finished_d = content_data["finished_d"] = defer.Deferred()
        args = [client, session, content_name, content_data]
        finished_d.addCallbacks(self._finishedCb, self._finishedEb, args, None, args)
        defer.returnValue(True)

    def jingleHandler(self, client, action, session, content_name, desc_elt):
        content_data = session["contents"][content_name]
        application_data = content_data["application_data"]
        if action in (self._j.A_ACCEPTED_ACK, self._j.A_SESSION_INITIATE):
            pass
        elif action == self._j.A_SESSION_ACCEPT:
            assert not "stream_object" in content_data
            content_data["stream_object"] = application_data["stream_object"]
            finished_d = content_data["finished_d"] = defer.Deferred()
            args = [client, session, content_name, content_data]
            finished_d.addCallbacks(self._finishedCb, self._finishedEb, args, None, args)
        else:
            log.warning(u"FIXME: unmanaged action {}".format(action))
        return desc_elt

    def _finishedCb(self, __, client, session, content_name, content_data):
        log.info(u"Pipe transfer completed")
        self._j.contentTerminate(client, session, content_name)
        content_data["stream_object"].stopStream()

    def _finishedEb(self, failure, client, session, content_name, content_data):
        log.warning(u"Error while streaming pipe: {}".format(failure))
        self._j.contentTerminate(
            client, session, content_name, reason=self._j.REASON_FAILED_TRANSPORT
        )
        content_data["stream_object"].stopStream()

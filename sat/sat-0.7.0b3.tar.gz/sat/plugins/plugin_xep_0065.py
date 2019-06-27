#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0065

# Copyright (C)
# 2002, 2003, 2004   Dave Smith (dizzyd@jabber.org)
# 2007, 2008         Fabio Forno (xmpp:ff@jabber.bluendo.com)
# 2009-2019 Jérôme Poisson (goffi@goffi.org)

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

# --

# This module is based on proxy65 (http://code.google.com/p/proxy65),
# originaly written by David Smith and modified by Fabio Forno.
# It is sublicensed under AGPL v3 (or any later version) as allowed by the original
# license.

# --

# Here is a copy of the original license:

# Copyright (C)
# 2002-2004   Dave Smith (dizzyd@jabber.org)
# 2007-2008   Fabio Forno (xmpp:ff@jabber.bluendo.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.tools import sat_defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import error as internet_error
from twisted.words.protocols.jabber import error as jabber_error
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import xmlstream
from twisted.internet import defer
from collections import namedtuple
import struct
import hashlib
import uuid

from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

from wokkel import disco, iwokkel


PLUGIN_INFO = {
    C.PI_NAME: "XEP 0065 Plugin",
    C.PI_IMPORT_NAME: "XEP-0065",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0065"],
    C.PI_DEPENDENCIES: ["IP"],
    C.PI_RECOMMENDATIONS: ["NAT-PORT"],
    C.PI_MAIN: "XEP_0065",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of SOCKS5 Bytestreams"""),
}

IQ_SET = '/iq[@type="set"]'
NS_BS = "http://jabber.org/protocol/bytestreams"
BS_REQUEST = IQ_SET + '/query[@xmlns="' + NS_BS + '"]'
TIMER_KEY = "timer"
DEFER_KEY = "finished"  # key of the deferred used to track session end
SERVER_STARTING_PORT = (
    0
)  # starting number for server port search (0 to ask automatic attribution)

# priorities are candidates local priorities, must be a int between 0 and 65535
PRIORITY_BEST_DIRECT = 10000
PRIORITY_DIRECT = 5000
PRIORITY_ASSISTED = 1000
PRIORITY_PROXY = 0.2  # proxy is the last option for s5b
CANDIDATE_DELAY = 0.2  # see XEP-0260 §4
CANDIDATE_DELAY_PROXY = 0.2  # additional time for proxy types (see XEP-0260 §4 note 3)

TIMEOUT = 300  # maxium time between session creation and stream start

# XXX: by default eveything is automatic
# TODO: use these params to force use of specific proxy/port/IP
# PARAMS = """
#     <params>
#     <general>
#     <category name="File Transfer">
#         <param name="Force IP" type="string" />
#         <param name="Force Port" type="int" constraint="1;65535" />
#     </category>
#     </general>
#     <individual>
#     <category name="File Transfer">
#         <param name="Force Proxy" value="" type="string" />
#         <param name="Force Proxy host" value="" type="string" />
#         <param name="Force Proxy port" value="" type="int" constraint="1;65535" />
#     </category>
#     </individual>
#     </params>
#     """

(
    STATE_INITIAL,
    STATE_AUTH,
    STATE_REQUEST,
    STATE_READY,
    STATE_AUTH_USERPASS,
    STATE_CLIENT_INITIAL,
    STATE_CLIENT_AUTH,
    STATE_CLIENT_REQUEST,
) = xrange(8)

SOCKS5_VER = 0x05

ADDR_IPV4 = 0x01
ADDR_DOMAINNAME = 0x03
ADDR_IPV6 = 0x04

CMD_CONNECT = 0x01
CMD_BIND = 0x02
CMD_UDPASSOC = 0x03

AUTHMECH_ANON = 0x00
AUTHMECH_USERPASS = 0x02
AUTHMECH_INVALID = 0xFF

REPLY_SUCCESS = 0x00
REPLY_GENERAL_FAILUR = 0x01
REPLY_CONN_NOT_ALLOWED = 0x02
REPLY_NETWORK_UNREACHABLE = 0x03
REPLY_HOST_UNREACHABLE = 0x04
REPLY_CONN_REFUSED = 0x05
REPLY_TTL_EXPIRED = 0x06
REPLY_CMD_NOT_SUPPORTED = 0x07
REPLY_ADDR_NOT_SUPPORTED = 0x08


ProxyInfos = namedtuple("ProxyInfos", ["host", "jid", "port"])


class Candidate(object):
    def __init__(
        self,
        host,
        port,
        type_,
        priority,
        jid_,
        id_=None,
        priority_local=False,
        factory=None,
    ):
        """
        @param host(unicode): host IP or domain
        @param port(int): port
        @param type_(unicode): stream type (one of XEP_0065.TYPE_*)
        @param priority(int): priority
        @param jid_(jid.JID): jid
        @param id_(None, id_): Candidate ID, or None to generate
        @param priority_local(bool): if True, priority is used as local priority,
            else priority is used as global one (and local priority is set to 0)
        """
        assert isinstance(jid_, jid.JID)
        self.host, self.port, self.type, self.jid = (host, int(port), type_, jid_)
        self.id = id_ if id_ is not None else unicode(uuid.uuid4())
        if priority_local:
            self._local_priority = int(priority)
            self._priority = self.calculatePriority()
        else:
            self._local_priority = 0
            self._priority = int(priority)
        self.factory = factory

    def discard(self):
        """Disconnect a candidate if it is connected

        Used to disconnect tryed client when they are discarded
        """
        log.debug(u"Discarding {}".format(self))
        try:
            self.factory.discard()
        except AttributeError:
            pass  # no discard for Socks5ServerFactory

    @property
    def local_priority(self):
        return self._local_priority

    @property
    def priority(self):
        return self._priority

    def __str__(self):
        # similar to __unicode__ but we don't show jid and we encode id
        return "Candidate ({0.priority}): host={0.host} port={0.port} type={0.type}{id}".format(
            self,
            id=u" id={}".format(self.id if self.id is not None else u"").encode(
                "utf-8", "ignore"
            ),
        )

    def __unicode__(self):
        return u"Candidate ({0.priority}): host={0.host} port={0.port} jid={0.jid} type={0.type}{id}".format(
            self, id=u" id={}".format(self.id if self.id is not None else u"")
        )

    def __eq__(self, other):
        # self.id is is not used in __eq__ as the same candidate can have
        # different ids if proposed by initiator or responder
        try:
            return (
                self.host == other.host
                and self.port == other.port
                and self.jid == other.jid
            )
        except (AttributeError, TypeError):
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def calculatePriority(self):
        """Calculate candidate priority according to XEP-0260 §2.2


        @return (int): priority
        """
        if self.type == XEP_0065.TYPE_DIRECT:
            multiplier = 126
        elif self.type == XEP_0065.TYPE_ASSISTED:
            multiplier = 120
        elif self.type == XEP_0065.TYPE_TUNEL:
            multiplier = 110
        elif self.type == XEP_0065.TYPE_PROXY:
            multiplier = 10
        else:
            raise exceptions.InternalError(u"Unknown {} type !".format(self.type))
        return 2 ** 16 * multiplier + self._local_priority

    def activate(self, client, sid, peer_jid, local_jid):
        """Activate the proxy candidate

        Send activation request as explained in XEP-0065 § 6.3.5
        Must only be used with proxy candidates
        @param sid(unicode): session id (same as for getSessionHash)
        @param peer_jid(jid.JID): jid of the other peer
        @return (D(domish.Element)): IQ result (or error)
        """
        assert self.type == XEP_0065.TYPE_PROXY
        iq_elt = client.IQ()
        iq_elt["from"] = local_jid.full()
        iq_elt["to"] = self.jid.full()
        query_elt = iq_elt.addElement((NS_BS, "query"))
        query_elt["sid"] = sid
        query_elt.addElement("activate", content=peer_jid.full())
        return iq_elt.send()

    def startTransfer(self, session_hash=None):
        if self.type == XEP_0065.TYPE_PROXY:
            chunk_size = 4096  # Prosody's proxy reject bigger chunks by default
        else:
            chunk_size = None
        self.factory.startTransfer(session_hash, chunk_size=chunk_size)


def getSessionHash(requester_jid, target_jid, sid):
    """Calculate SHA1 Hash according to XEP-0065 §5.3.2

    @param requester_jid(jid.JID): jid of the requester (the one which activate the proxy)
    @param target_jid(jid.JID): jid of the target
    @param sid(unicode): session id
    @return (str): hash
    """
    return hashlib.sha1(
        (sid + requester_jid.full() + target_jid.full()).encode("utf-8")
    ).hexdigest()


class SOCKSv5(protocol.Protocol):
    CHUNK_SIZE = 2 ** 16

    def __init__(self, session_hash=None):
        """
        @param session_hash(str): hash of the session
            must only be used in client mode
        """
        self.connection = defer.Deferred()  # called when connection/auth is done
        if session_hash is not None:
            self.server_mode = False
            self._session_hash = session_hash
            self.state = STATE_CLIENT_INITIAL
        else:
            self.server_mode = True
            self.state = STATE_INITIAL
        self.buf = ""
        self.supportedAuthMechs = [AUTHMECH_ANON]
        self.supportedAddrs = [ADDR_DOMAINNAME]
        self.enabledCommands = [CMD_CONNECT]
        self.peersock = None
        self.addressType = 0
        self.requestType = 0
        self._stream_object = None
        self.active = False  # set to True when protocol is actually used for transfer
        # used by factories to know when the finished Deferred can be triggered

    @property
    def stream_object(self):
        if self._stream_object is None:
            self._stream_object = self.getSession()["stream_object"]
            if self.server_mode:
                self._stream_object.registerProducer(self.transport, True)
        return self._stream_object

    def getSession(self):
        """Return session associated with this candidate

        @return (dict): session data
        """
        if self.server_mode:
            return self.factory.getSession(self._session_hash)
        else:
            return self.factory.getSession()

    def _startNegotiation(self):
        log.debug("starting negotiation (client mode)")
        self.state = STATE_CLIENT_AUTH
        self.transport.write(struct.pack("!3B", SOCKS5_VER, 1, AUTHMECH_ANON))

    def _parseNegotiation(self):
        try:
            # Parse out data
            ver, nmethod = struct.unpack("!BB", self.buf[:2])
            methods = struct.unpack("%dB" % nmethod, self.buf[2 : nmethod + 2])

            # Ensure version is correct
            if ver != 5:
                self.transport.write(struct.pack("!BB", SOCKS5_VER, AUTHMECH_INVALID))
                self.transport.loseConnection()
                return

            # Trim off front of the buffer
            self.buf = self.buf[nmethod + 2 :]

            # Check for supported auth mechs
            for m in self.supportedAuthMechs:
                if m in methods:
                    # Update internal state, according to selected method
                    if m == AUTHMECH_ANON:
                        self.state = STATE_REQUEST
                    elif m == AUTHMECH_USERPASS:
                        self.state = STATE_AUTH_USERPASS
                    # Complete negotiation w/ this method
                    self.transport.write(struct.pack("!BB", SOCKS5_VER, m))
                    return

            # No supported mechs found, notify client and close the connection
            log.warning(u"Unsupported authentication mechanism")
            self.transport.write(struct.pack("!BB", SOCKS5_VER, AUTHMECH_INVALID))
            self.transport.loseConnection()
        except struct.error:
            pass

    def _parseUserPass(self):
        try:
            # Parse out data
            ver, ulen = struct.unpack("BB", self.buf[:2])
            uname, = struct.unpack("%ds" % ulen, self.buf[2 : ulen + 2])
            plen, = struct.unpack("B", self.buf[ulen + 2])
            password, = struct.unpack("%ds" % plen, self.buf[ulen + 3 : ulen + 3 + plen])
            # Trim off fron of the buffer
            self.buf = self.buf[3 + ulen + plen :]
            # Fire event to authenticate user
            if self.authenticateUserPass(uname, password):
                # Signal success
                self.state = STATE_REQUEST
                self.transport.write(struct.pack("!BB", SOCKS5_VER, 0x00))
            else:
                # Signal failure
                self.transport.write(struct.pack("!BB", SOCKS5_VER, 0x01))
                self.transport.loseConnection()
        except struct.error:
            pass

    def sendErrorReply(self, errorcode):
        # Any other address types are not supported
        result = struct.pack("!BBBBIH", SOCKS5_VER, errorcode, 0, 1, 0, 0)
        self.transport.write(result)
        self.transport.loseConnection()

    def _parseRequest(self):
        try:
            # Parse out data and trim buffer accordingly
            ver, cmd, rsvd, self.addressType = struct.unpack("!BBBB", self.buf[:4])

            # Ensure we actually support the requested address type
            if self.addressType not in self.supportedAddrs:
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Deal with addresses
            if self.addressType == ADDR_IPV4:
                addr, port = struct.unpack("!IH", self.buf[4:10])
                self.buf = self.buf[10:]
            elif self.addressType == ADDR_DOMAINNAME:
                nlen = ord(self.buf[4])
                addr, port = struct.unpack("!%dsH" % nlen, self.buf[5:])
                self.buf = self.buf[7 + len(addr) :]
            else:
                # Any other address types are not supported
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Ensure command is supported
            if cmd not in self.enabledCommands:
                # Send a not supported error
                self.sendErrorReply(REPLY_CMD_NOT_SUPPORTED)
                return

            # Process the command
            if cmd == CMD_CONNECT:
                self.connectRequested(addr, port)
            elif cmd == CMD_BIND:
                self.bindRequested(addr, port)
            else:
                # Any other command is not supported
                self.sendErrorReply(REPLY_CMD_NOT_SUPPORTED)

        except struct.error:
            # The buffer is probably not complete, we need to wait more
            return None

    def _makeRequest(self):
        hash_ = self._session_hash
        request = struct.pack(
            "!5B%dsH" % len(hash_),
            SOCKS5_VER,
            CMD_CONNECT,
            0,
            ADDR_DOMAINNAME,
            len(hash_),
            hash_,
            0,
        )
        self.transport.write(request)
        self.state = STATE_CLIENT_REQUEST

    def _parseRequestReply(self):
        try:
            ver, rep, rsvd, self.addressType = struct.unpack("!BBBB", self.buf[:4])
            # Ensure we actually support the requested address type
            if self.addressType not in self.supportedAddrs:
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Deal with addresses
            if self.addressType == ADDR_IPV4:
                addr, port = struct.unpack("!IH", self.buf[4:10])
                self.buf = self.buf[10:]
            elif self.addressType == ADDR_DOMAINNAME:
                nlen = ord(self.buf[4])
                addr, port = struct.unpack("!%dsH" % nlen, self.buf[5:])
                self.buf = self.buf[7 + len(addr) :]
            else:
                # Any other address types are not supported
                self.sendErrorReply(REPLY_ADDR_NOT_SUPPORTED)
                return

            # Ensure reply is OK
            if rep != REPLY_SUCCESS:
                self.loseConnection()
                return

            self.state = STATE_READY
            self.connection.callback(None)

        except struct.error:
            # The buffer is probably not complete, we need to wait more
            return None

    def connectionMade(self):
        log.debug(
            u"Socks5 connectionMade (mode = {})".format(
                "server" if self.state == STATE_INITIAL else "client"
            )
        )
        if self.state == STATE_CLIENT_INITIAL:
            self._startNegotiation()

    def connectRequested(self, addr, port):
        # Check that this session is expected
        if not self.factory.addToSession(addr, self):
            self.sendErrorReply(REPLY_CONN_REFUSED)
            log.warning(
                u"Unexpected connection request received from {host}".format(
                    host=self.transport.getPeer().host
                )
            )
            return
        self._session_hash = addr
        self.connectCompleted(addr, 0)

    def startTransfer(self, chunk_size):
        """Callback called when the result iq is received

        @param chunk_size(None, int): size of the buffer, or None for default
        """
        self.active = True
        if chunk_size is not None:
            self.CHUNK_SIZE = chunk_size
        log.debug(u"Starting file transfer")
        d = self.stream_object.startStream(self.transport)
        d.addCallback(self.streamFinished)

    def streamFinished(self, d):
        log.info(_("File transfer completed, closing connection"))
        self.transport.loseConnection()

    def connectCompleted(self, remotehost, remoteport):
        if self.addressType == ADDR_IPV4:
            result = struct.pack(
                "!BBBBIH", SOCKS5_VER, REPLY_SUCCESS, 0, 1, remotehost, remoteport
            )
        elif self.addressType == ADDR_DOMAINNAME:
            result = struct.pack(
                "!BBBBB%dsH" % len(remotehost),
                SOCKS5_VER,
                REPLY_SUCCESS,
                0,
                ADDR_DOMAINNAME,
                len(remotehost),
                remotehost,
                remoteport,
            )
        self.transport.write(result)
        self.state = STATE_READY

    def bindRequested(self, addr, port):
        pass

    def authenticateUserPass(self, user, passwd):
        # FIXME: implement authentication and remove the debug printing a password
        log.debug(u"User/pass: %s/%s" % (user, passwd))
        return True

    def dataReceived(self, buf):
        if self.state == STATE_READY:
            # Everything is set, we just have to write the incoming data
            self.stream_object.write(buf)
            if not self.active:
                self.active = True
                self.getSession()[TIMER_KEY].cancel()
            return

        self.buf = self.buf + buf
        if self.state == STATE_INITIAL:
            self._parseNegotiation()
        if self.state == STATE_AUTH_USERPASS:
            self._parseUserPass()
        if self.state == STATE_REQUEST:
            self._parseRequest()
        if self.state == STATE_CLIENT_REQUEST:
            self._parseRequestReply()
        if self.state == STATE_CLIENT_AUTH:
            ver, method = struct.unpack("!BB", buf)
            self.buf = self.buf[2:]
            if ver != SOCKS5_VER or method != AUTHMECH_ANON:
                self.transport.loseConnection()
            else:
                self._makeRequest()

    def connectionLost(self, reason):
        log.debug(u"Socks5 connection lost: {}".format(reason.value))
        if self.state != STATE_READY:
            self.connection.errback(reason)
        if self.server_mode:
            self.factory.removeFromSession(self._session_hash, self, reason)


class Socks5ServerFactory(protocol.ServerFactory):
    protocol = SOCKSv5

    def __init__(self, parent):
        """
        @param parent(XEP_0065): XEP_0065 parent instance
        """
        self.parent = parent

    def getSession(self, session_hash):
        return self.parent.getSession(None, session_hash)

    def startTransfer(self, session_hash, chunk_size=None):
        session = self.getSession(session_hash)
        try:
            protocol = session["protocols"][0]
        except (KeyError, IndexError):
            log.error(u"Can't start file transfer, can't find protocol")
        else:
            session[TIMER_KEY].cancel()
            protocol.startTransfer(chunk_size)

    def addToSession(self, session_hash, protocol):
        """Check is session_hash is valid, and associate protocol with it

        the session will be associated to the corresponding candidate
        @param session_hash(str): hash of the session
        @param protocol(SOCKSv5): protocol instance
        @param return(bool): True if hash was valid (i.e. expected), False else
        """
        try:
            session_data = self.getSession(session_hash)
        except KeyError:
            return False
        else:
            session_data.setdefault("protocols", []).append(protocol)
            return True

    def removeFromSession(self, session_hash, protocol, reason):
        """Remove a protocol from session_data

        There can be several protocol instances while candidates are tried, they
        have removed when candidate connection is closed
        @param session_hash(str): hash of the session
        @param protocol(SOCKSv5): protocol instance
        @param reason(failure.Failure): reason of the removal
        """
        try:
            protocols = self.getSession(session_hash)["protocols"]
            protocols.remove(protocol)
        except (KeyError, ValueError):
            log.error(u"Protocol not found in session while it should be there")
        else:
            if protocol.active:
                # The active protocol has been removed, session is finished
                if reason.check(internet_error.ConnectionDone):
                    self.getSession(session_hash)[DEFER_KEY].callback(None)
                else:
                    self.getSession(session_hash)[DEFER_KEY].errback(reason)


class Socks5ClientFactory(protocol.ClientFactory):
    protocol = SOCKSv5

    def __init__(self, client, parent, session, session_hash):
        """Init the Client Factory

        @param session(dict): session data
        @param session_hash(unicode): hash used for peer_connection
            hash is the same as hostname computed in XEP-0065 § 5.3.2 #1
        """
        self.session = session
        self.session_hash = session_hash
        self.client = client
        self.connection = defer.Deferred()
        self._protocol_instance = None
        self.connector = None

    def discard(self):
        """Disconnect the client

        Also set a discarded flag, which avoid to call the session Deferred
        """
        self.connector.disconnect()

    def getSession(self):
        return self.session

    def startTransfer(self, __=None, chunk_size=None):
        self.session[TIMER_KEY].cancel()
        self._protocol_instance.startTransfer(chunk_size)

    def clientConnectionFailed(self, connector, reason):
        log.debug(u"Connection failed")
        self.connection.errback(reason)

    def clientConnectionLost(self, connector, reason):
        log.debug(_(u"Socks 5 client connection lost (reason: %s)") % reason.value)
        if self._protocol_instance.active:
            # This one was used for the transfer, than mean that
            # the Socks5 session is finished
            if reason.check(internet_error.ConnectionDone):
                self.getSession()[DEFER_KEY].callback(None)
            else:
                self.getSession()[DEFER_KEY].errback(reason)
        self._protocol_instance = None

    def buildProtocol(self, addr):
        log.debug(("Socks 5 client connection started"))
        p = self.protocol(session_hash=self.session_hash)
        p.factory = self
        p.connection.chainDeferred(self.connection)
        self._protocol_instance = p
        return p


class XEP_0065(object):
    NAMESPACE = NS_BS
    TYPE_DIRECT = "direct"
    TYPE_ASSISTED = "assisted"
    TYPE_TUNEL = "tunel"
    TYPE_PROXY = "proxy"
    Candidate = Candidate

    def __init__(self, host):
        log.info(_("Plugin XEP_0065 initialization"))
        self.host = host

        # session data
        self.hash_clients_map = {}  # key: hash of the transfer session, value: session data
        self._cache_proxies = {}  # key: server jid, value: proxy data

        # misc data
        self._server_factory = None
        self._external_port = None

        # plugins shortcuts
        self._ip = self.host.plugins["IP"]
        try:
            self._np = self.host.plugins["NAT-PORT"]
        except KeyError:
            log.debug(u"NAT Port plugin not available")
            self._np = None

        # parameters
        # XXX: params are not used for now, but they may be used in the futur to force proxy/IP
        # host.memory.updateParams(PARAMS)

    def getHandler(self, client):
        return XEP_0065_handler(self)

    def profileConnected(self, client):
        client.xep_0065_sid_session = {}  # key: stream_id, value: session_data(dict)
        client._s5b_sessions = {}

    def getSessionHash(self, from_jid, to_jid, sid):
        return getSessionHash(from_jid, to_jid, sid)

    def getSocks5ServerFactory(self):
        """Return server factory

        The server is created if it doesn't exists yet
        self._server_factory_port is set on server creation
        """

        if self._server_factory is None:
            self._server_factory = Socks5ServerFactory(self)
            for port in xrange(SERVER_STARTING_PORT, 65356):
                try:
                    listening_port = reactor.listenTCP(port, self._server_factory)
                except internet_error.CannotListenError as e:
                    log.debug(
                        u"Cannot listen on port {port}: {err_msg}{err_num}".format(
                            port=port,
                            err_msg=e.socketError.strerror,
                            err_num=u" (error code: {})".format(e.socketError.errno),
                        )
                    )
                else:
                    self._server_factory_port = listening_port.getHost().port
                    break

            log.info(
                _("Socks5 Stream server launched on port {}").format(
                    self._server_factory_port
                )
            )
        return self._server_factory

    @defer.inlineCallbacks
    def getProxy(self, client, local_jid):
        """Return the proxy available for this profile

        cache is used between clients using the same server
        @param local_jid(jid.JID): same as for [getCandidates]
        @return ((D)(ProxyInfos, None)): Found proxy infos,
            or None if not acceptable proxy is found
        @raise exceptions.NotFound: no Proxy found
        """

        def notFound(server):
            log.info(u"No proxy found on this server")
            self._cache_proxies[server] = None
            raise exceptions.NotFound

        server = client.host if client.is_component else client.jid.host
        try:
            defer.returnValue(self._cache_proxies[server])
        except KeyError:
            pass
        try:
            proxy = (
                yield self.host.findServiceEntities(client, "proxy", "bytestreams")
            ).pop()
        except (defer.CancelledError, StopIteration, KeyError):
            notFound(server)
        iq_elt = client.IQ("get")
        iq_elt["from"] = local_jid.full()
        iq_elt["to"] = proxy.full()
        iq_elt.addElement((NS_BS, "query"))

        try:
            result_elt = yield iq_elt.send()
        except jabber_error.StanzaError as failure:
            log.warning(
                u"Error while requesting proxy info on {jid}: {error}".format(
                    proxy.full(), failure
                )
            )
            notFound(server)

        try:
            query_elt = result_elt.elements(NS_BS, "query").next()
            streamhost_elt = query_elt.elements(NS_BS, "streamhost").next()
            host = streamhost_elt["host"]
            jid_ = streamhost_elt["jid"]
            port = streamhost_elt["port"]
            if not all((host, jid, port)):
                raise KeyError
            jid_ = jid.JID(jid_)
        except (StopIteration, KeyError, RuntimeError, jid.InvalidFormat, AttributeError):
            log.warning(u"Invalid proxy data received from {}".format(proxy.full()))
            notFound(server)

        proxy_infos = self._cache_proxies[server] = ProxyInfos(host, jid_, port)
        log.info(u"Proxy found: {}".format(proxy_infos))
        defer.returnValue(proxy_infos)

    @defer.inlineCallbacks
    def _getNetworkData(self, client):
        """Retrieve information about network

        @param client: %(doc_client)s
        @return (D(tuple[local_port, external_port, local_ips, external_ip])): network data
        """
        self.getSocks5ServerFactory()
        local_port = self._server_factory_port
        external_ip = yield self._ip.getExternalIP(client)
        local_ips = yield self._ip.getLocalIPs(client)

        if external_ip is not None and self._external_port is None:
            if external_ip != local_ips[0]:
                log.info(u"We are probably behind a NAT")
                if self._np is None:
                    log.warning(u"NAT port plugin not available, we can't map port")
                else:
                    ext_port = yield self._np.mapPort(
                        local_port, desc=u"SaT socks5 stream"
                    )
                    if ext_port is None:
                        log.warning(u"Can't map NAT port")
                    else:
                        self._external_port = ext_port

        defer.returnValue((local_port, self._external_port, local_ips, external_ip))

    @defer.inlineCallbacks
    def getCandidates(self, client, local_jid):
        """Return a list of our stream candidates

        @param local_jid(jid.JID): jid to use as local jid
            This is needed for client which can be addressed with a different jid than
            client.jid if a local part is used (e.g. piotr@file.example.net where
            client.jid would be file.example.net)
        @return (D(list[Candidate])): list of candidates, ordered by priority
        """
        server_factory = yield self.getSocks5ServerFactory()
        local_port, ext_port, local_ips, external_ip = yield self._getNetworkData(client)
        try:
            proxy = yield self.getProxy(client, local_jid)
        except exceptions.NotFound:
            proxy = None

        # its time to gather the candidates
        candidates = []

        # first the direct ones

        # the preferred direct connection
        ip = local_ips.pop(0)
        candidates.append(
            Candidate(
                ip,
                local_port,
                XEP_0065.TYPE_DIRECT,
                PRIORITY_BEST_DIRECT,
                local_jid,
                priority_local=True,
                factory=server_factory,
            )
        )
        for ip in local_ips:
            candidates.append(
                Candidate(
                    ip,
                    local_port,
                    XEP_0065.TYPE_DIRECT,
                    PRIORITY_DIRECT,
                    local_jid,
                    priority_local=True,
                    factory=server_factory,
                )
            )

        # then the assisted one
        if ext_port is not None:
            candidates.append(
                Candidate(
                    external_ip,
                    ext_port,
                    XEP_0065.TYPE_ASSISTED,
                    PRIORITY_ASSISTED,
                    local_jid,
                    priority_local=True,
                    factory=server_factory,
                )
            )

        # finally the proxy
        if proxy:
            candidates.append(
                Candidate(
                    proxy.host,
                    proxy.port,
                    XEP_0065.TYPE_PROXY,
                    PRIORITY_PROXY,
                    proxy.jid,
                    priority_local=True,
                )
            )

        # should be already sorted, but just in case the priorities get weird
        candidates.sort(key=lambda c: c.priority, reverse=True)
        defer.returnValue(candidates)

    def _addConnector(self, connector, candidate):
        """Add connector used to connect to candidate, and return client factory's connection Deferred

        the connector can be used to disconnect the candidate, and returning the factory's connection Deferred allow to wait for connection completion
        @param connector: a connector implementing IConnector
        @param candidate(Candidate): candidate linked to the connector
        @return (D): Deferred fired when factory connection is done or has failed
        """
        candidate.factory.connector = connector
        return candidate.factory.connection

    def connectCandidate(
        self, client, candidate, session_hash, peer_session_hash=None, delay=None
    ):
        """Connect to a candidate

        Connection will be done with a Socks5ClientFactory
        @param candidate(Candidate): candidate to connect to
        @param session_hash(unicode): hash of the session
            hash is the same as hostname computed in XEP-0065 § 5.3.2 #1
        @param peer_session_hash(unicode, None): hash used with the peer
            None to use session_hash.
            None must be used in 2 cases:
                - when XEP-0065 is used with XEP-0096
                - when a peer connect to a proxy *he proposed himself*
            in practice, peer_session_hash is only used by tryCandidates
        @param delay(None, float): optional delay to wait before connection, in seconds
        @return (D): Deferred launched when TCP connection + Socks5 connection is done
        """
        if peer_session_hash is None:
            # for XEP-0065, only one hash is needed
            peer_session_hash = session_hash
        session = self.getSession(client, session_hash)
        factory = Socks5ClientFactory(client, self, session, peer_session_hash)
        candidate.factory = factory
        if delay is None:
            d = defer.succeed(candidate.host)
        else:
            d = sat_defer.DelayedDeferred(delay, candidate.host)
        d.addCallback(reactor.connectTCP, candidate.port, factory)
        d.addCallback(self._addConnector, candidate)
        return d

    def tryCandidates(
        self,
        client,
        candidates,
        session_hash,
        peer_session_hash,
        connection_cb=None,
        connection_eb=None,
    ):
        defers_list = []

        for candidate in candidates:
            delay = CANDIDATE_DELAY * len(defers_list)
            if candidate.type == XEP_0065.TYPE_PROXY:
                delay += CANDIDATE_DELAY_PROXY
            d = self.connectCandidate(
                client, candidate, session_hash, peer_session_hash, delay
            )
            if connection_cb is not None:
                d.addCallback(
                    lambda __, candidate=candidate, client=client: connection_cb(
                        client, candidate
                    )
                )
            if connection_eb is not None:
                d.addErrback(connection_eb, client, candidate)
            defers_list.append(d)

        return defers_list

    def getBestCandidate(self, client, candidates, session_hash, peer_session_hash=None):
        """Get best candidate (according to priority) which can connect

        @param candidates(iterable[Candidate]): candidates to test
        @param session_hash(unicode): hash of the session
            hash is the same as hostname computed in XEP-0065 § 5.3.2 #1
        @param peer_session_hash(unicode, None): hash of the other peer
            only useful for XEP-0260, must be None for XEP-0065 streamhost candidates
        @return (D(None, Candidate)): best candidate or None if none can connect
        """
        defer_candidates = None

        def connectionCb(client, candidate):
            log.info(u"Connection of {} successful".format(unicode(candidate)))
            for idx, other_candidate in enumerate(candidates):
                try:
                    if other_candidate.priority < candidate.priority:
                        log.debug(u"Cancelling {}".format(other_candidate))
                        defer_candidates[idx].cancel()
                except AttributeError:
                    assert other_candidate is None

        def connectionEb(failure, client, candidate):
            if failure.check(defer.CancelledError):
                log.debug(u"Connection of {} has been cancelled".format(candidate))
            else:
                log.info(
                    u"Connection of {candidate} Failed: {error}".format(
                        candidate=candidate, error=failure.value
                    )
                )
            candidates[candidates.index(candidate)] = None

        def allTested(self):
            log.debug(u"All candidates have been tested")
            good_candidates = [c for c in candidates if c]
            return good_candidates[0] if good_candidates else None

        defer_candidates = self.tryCandidates(
            client,
            candidates,
            session_hash,
            peer_session_hash,
            connectionCb,
            connectionEb,
        )
        d_list = defer.DeferredList(defer_candidates)
        d_list.addCallback(allTested)
        return d_list

    def _timeOut(self, session_hash, client):
        """Called when stream was not started quickly enough

        @param session_hash(str): hash as returned by getSessionHash
        @param client: %(doc_client)s
        """
        log.info(u"Socks5 Bytestream: TimeOut reached")
        session = self.getSession(client, session_hash)
        session[DEFER_KEY].errback(exceptions.TimeOutError)

    def killSession(self, failure_, session_hash, sid, client):
        """Clean the current session

        @param session_hash(str): hash as returned by getSessionHash
        @param sid(None, unicode): session id
            or None if self.xep_0065_sid_session was not used
        @param client: %(doc_client)s
        @param failure_(None, failure.Failure): None if eveything was fine, a failure else
        @return (None, failure.Failure): failure_ is returned
        """
        log.debug(
            u"Cleaning session with hash {hash}{id}: {reason}".format(
                hash=session_hash,
                reason="" if failure_ is None else failure_.value,
                id="" if sid is None else u" (id: {})".format(sid),
            )
        )

        try:
            assert self.hash_clients_map[session_hash] == client
            del self.hash_clients_map[session_hash]
        except KeyError:
            pass

        if sid is not None:
            try:
                del client.xep_0065_sid_session[sid]
            except KeyError:
                log.warning(u"Session id {} is unknown".format(sid))

        try:
            session_data = client._s5b_sessions[session_hash]
        except KeyError:
            log.warning(u"There is no session with this hash")
            return
        else:
            del client._s5b_sessions[session_hash]

        try:
            session_data["timer"].cancel()
        except (internet_error.AlreadyCalled, internet_error.AlreadyCancelled):
            pass

        return failure_

    def startStream(self, client, stream_object, local_jid, to_jid, sid):
        """Launch the stream workflow

        @param streamProducer: stream_object to use
        @param local_jid(jid.JID): same as for [getCandidates]
        @param to_jid: JID of the recipient
        @param sid: Stream session id
        @param successCb: method to call when stream successfuly finished
        @param failureCb: method to call when something goes wrong
        @return (D): Deferred fired when session is finished
        """
        session_data = self._createSession(
            client, stream_object, local_jid, to_jid, sid, True)

        session_data[client] = client

        def gotCandidates(candidates):
            session_data["candidates"] = candidates
            iq_elt = client.IQ()
            iq_elt["from"] = local_jid.full()
            iq_elt["to"] = to_jid.full()
            query_elt = iq_elt.addElement((NS_BS, "query"))
            query_elt["mode"] = "tcp"
            query_elt["sid"] = sid

            for candidate in candidates:
                streamhost = query_elt.addElement("streamhost")
                streamhost["host"] = candidate.host
                streamhost["port"] = str(candidate.port)
                streamhost["jid"] = candidate.jid.full()
                log.debug(u"Candidate proposed: {}".format(candidate))

            d = iq_elt.send()
            args = [client, session_data, local_jid]
            d.addCallbacks(self._IQNegotiationCb, self._IQNegotiationEb, args, None, args)

        self.getCandidates(client, local_jid).addCallback(gotCandidates)
        return session_data[DEFER_KEY]

    def _IQNegotiationCb(self, iq_elt, client, session_data, local_jid):
        """Called when the result of open iq is received

        @param session_data(dict): data of the session
        @param client: %(doc_client)s
        @param iq_elt(domish.Element): <iq> result
        """
        try:
            query_elt = iq_elt.elements(NS_BS, "query").next()
            streamhost_used_elt = query_elt.elements(NS_BS, "streamhost-used").next()
        except StopIteration:
            log.warning(u"No streamhost found in stream query")
            # FIXME: must clean session
            return

        streamhost_jid = jid.JID(streamhost_used_elt["jid"])
        try:
            candidate = (
                c for c in session_data["candidates"] if c.jid == streamhost_jid
            ).next()
        except StopIteration:
            log.warning(
                u"Candidate [{jid}] is unknown !".format(jid=streamhost_jid.full())
            )
            return
        else:
            log.info(u"Candidate choosed by target: {}".format(candidate))

        if candidate.type == XEP_0065.TYPE_PROXY:
            log.info(u"A Socks5 proxy is used")
            d = self.connectCandidate(client, candidate, session_data["hash"])
            d.addCallback(
                lambda __: candidate.activate(
                    client, session_data["id"], session_data["peer_jid"], local_jid
                )
            )
            d.addErrback(self._activationEb)
        else:
            d = defer.succeed(None)

        d.addCallback(lambda __: candidate.startTransfer(session_data["hash"]))

    def _activationEb(self, failure):
        log.warning(u"Proxy activation error: {}".format(failure.value))

    def _IQNegotiationEb(self, stanza_err, client, session_data, local_jid):
        log.warning(u"Socks5 transfer failed: {}".format(stanza_err.value))
        # FIXME: must clean session

    def createSession(self, *args, **kwargs):
        """like [_createSession] but return the session deferred instead of the whole session

        session deferred is fired when transfer is finished
        """
        return self._createSession(*args, **kwargs)[DEFER_KEY]

    def _createSession(self, client, stream_object, local_jid, to_jid, sid,
                       requester=False):
        """Called when a bytestream is imminent

        @param stream_object(iface.IStreamProducer): File object where data will be
            written
        @param to_jid(jid.JId): jid of the other peer
        @param sid(unicode): session id
        @param initiator(bool): if True, this session is create by initiator
        @return (dict): session data
        """
        if sid in client.xep_0065_sid_session:
            raise exceptions.ConflictError(u"A session with this id already exists !")
        if requester:
            session_hash = getSessionHash(local_jid, to_jid, sid)
            session_data = self._registerHash(client, session_hash, stream_object)
        else:
            session_hash = getSessionHash(to_jid, local_jid, sid)
            session_d = defer.Deferred()
            session_d.addBoth(self.killSession, session_hash, sid, client)
            session_data = client._s5b_sessions[session_hash] = {
                DEFER_KEY: session_d,
                TIMER_KEY: reactor.callLater(
                    TIMEOUT, self._timeOut, session_hash, client
                ),
            }
        client.xep_0065_sid_session[sid] = session_data
        session_data.update(
            {
                "id": sid,
                "local_jid": local_jid,
                "peer_jid": to_jid,
                "stream_object": stream_object,
                "hash": session_hash,
            }
        )

        return session_data

    def getSession(self, client, session_hash):
        """Return session data

        @param session_hash(unicode): hash of the session
            hash is the same as hostname computed in XEP-0065 § 5.3.2 #1
        @param client(None, SatXMPPClient): client of the peer
            None is used only if client is unknown (this is only the case
            for incoming request received by Socks5ServerFactory). None must
            only be used by Socks5ServerFactory.
            See comments below for details
        @return (dict): session data
        """
        if client is None:
            try:
                client = self.hash_clients_map[session_hash]
            except KeyError as e:
                log.warning(u"The requested session doesn't exists !")
                raise e
        return client._s5b_sessions[session_hash]

    def registerHash(self, *args, **kwargs):
        """like [_registerHash] but return the session deferred instead of the whole session
        session deferred is fired when transfer is finished
        """
        return self._registerHash(*args, **kwargs)[DEFER_KEY]

    def _registerHash(self, client, session_hash, stream_object):
        """Create a session_data associated to hash

        @param session_hash(str): hash of the session
        @param stream_object(iface.IStreamProducer, IConsumer, None): file-like object
            None if it will be filled later
        return (dict): session data
        """
        assert session_hash not in client._s5b_sessions
        session_d = defer.Deferred()
        session_d.addBoth(self.killSession, session_hash, None, client)
        session_data = client._s5b_sessions[session_hash] = {
            DEFER_KEY: session_d,
            TIMER_KEY: reactor.callLater(TIMEOUT, self._timeOut, session_hash, client),
        }

        if stream_object is not None:
            session_data["stream_object"] = stream_object

        assert session_hash not in self.hash_clients_map
        self.hash_clients_map[session_hash] = client

        return session_data

    def associateStreamObject(self, client, session_hash, stream_object):
        """Associate a stream object with  a session"""
        session_data = self.getSession(client, session_hash)
        assert "stream_object" not in session_data
        session_data["stream_object"] = stream_object

    def streamQuery(self, iq_elt, client):
        log.debug(u"BS stream query")

        iq_elt.handled = True

        query_elt = iq_elt.elements(NS_BS, "query").next()
        try:
            sid = query_elt["sid"]
        except KeyError:
            log.warning(u"Invalid bystreams request received")
            return client.sendError(iq_elt, "bad-request")

        streamhost_elts = list(query_elt.elements(NS_BS, "streamhost"))
        if not streamhost_elts:
            return client.sendError(iq_elt, "bad-request")

        try:
            session_data = client.xep_0065_sid_session[sid]
        except KeyError:
            log.warning(u"Ignoring unexpected BS transfer: {}".format(sid))
            return client.sendError(iq_elt, "not-acceptable")

        peer_jid = session_data["peer_jid"] = jid.JID(iq_elt["from"])

        candidates = []
        nb_sh = len(streamhost_elts)
        for idx, sh_elt in enumerate(streamhost_elts):
            try:
                host, port, jid_ = sh_elt["host"], sh_elt["port"], jid.JID(sh_elt["jid"])
            except KeyError:
                log.warning(u"malformed streamhost element")
                return client.sendError(iq_elt, "bad-request")
            priority = nb_sh - idx
            if jid_.userhostJID() != peer_jid.userhostJID():
                type_ = XEP_0065.TYPE_PROXY
            else:
                type_ = XEP_0065.TYPE_DIRECT
            candidates.append(Candidate(host, port, type_, priority, jid_))

        for candidate in candidates:
            log.info(u"Candidate proposed: {}".format(candidate))

        d = self.getBestCandidate(client, candidates, session_data["hash"])
        d.addCallback(self._ackStream, iq_elt, session_data, client)

    def _ackStream(self, candidate, iq_elt, session_data, client):
        if candidate is None:
            log.info("No streamhost candidate worked, we have to end negotiation")
            return client.sendError(iq_elt, "item-not-found")
        log.info(u"We choose: {}".format(candidate))
        result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = result_elt.addElement((NS_BS, "query"))
        query_elt["sid"] = session_data["id"]
        streamhost_used_elt = query_elt.addElement("streamhost-used")
        streamhost_used_elt["jid"] = candidate.jid.full()
        client.send(result_elt)


class XEP_0065_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            BS_REQUEST, self.plugin_parent.streamQuery, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_BS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

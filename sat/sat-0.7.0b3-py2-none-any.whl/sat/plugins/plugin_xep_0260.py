#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Jingle (XEP-0260)
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

log = getLogger(__name__)
from sat.core import exceptions
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
import uuid

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler


NS_JINGLE_S5B = "urn:xmpp:jingle:transports:s5b:1"

PLUGIN_INFO = {
    C.PI_NAME: "Jingle SOCKS5 Bytestreams",
    C.PI_IMPORT_NAME: "XEP-0260",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0260"],
    C.PI_DEPENDENCIES: ["XEP-0166", "XEP-0065"],
    C.PI_RECOMMENDATIONS: ["XEP-0261"],  # needed for fallback
    C.PI_MAIN: "XEP_0260",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Jingle SOCKS5 Bytestreams"""),
}


class ProxyError(Exception):
    def __str__(self):
        return "an error happened while trying to use the proxy"


class XEP_0260(object):
    # TODO: udp handling

    def __init__(self, host):
        log.info(_("plugin Jingle SOCKS5 Bytestreams"))
        self.host = host
        self._j = host.plugins["XEP-0166"]  # shortcut to access jingle
        self._s5b = host.plugins["XEP-0065"]  # and socks5 bytestream
        try:
            self._jingle_ibb = host.plugins["XEP-0261"]
        except KeyError:
            self._jingle_ibb = None
        self._j.registerTransport(NS_JINGLE_S5B, self._j.TRANSPORT_STREAMING, self, 100)

    def getHandler(self, client):
        return XEP_0260_handler()

    def _parseCandidates(self, transport_elt):
        """Parse <candidate> elements

        @param transport_elt(domish.Element): parent <transport> element
        @return (list[plugin_xep_0065.Candidate): list of parsed candidates
        """
        candidates = []
        for candidate_elt in transport_elt.elements(NS_JINGLE_S5B, "candidate"):
            try:
                cid = candidate_elt["cid"]
                host = candidate_elt["host"]
                jid_ = jid.JID(candidate_elt["jid"])
                port = int(candidate_elt.getAttribute("port", 1080))
                priority = int(candidate_elt["priority"])
                type_ = candidate_elt.getAttribute("type", self._s5b.TYPE_DIRECT)
            except (KeyError, ValueError):
                raise exceptions.DataError()
            candidate = self._s5b.Candidate(host, port, type_, priority, jid_, cid)
            candidates.append(candidate)
            # self._s5b.registerCandidate(candidate)
        return candidates

    def _buildCandidates(self, session, candidates, sid, session_hash, client, mode=None):
        """Build <transport> element with candidates

        @param session(dict): jingle session data
        @param candidates(iterator[plugin_xep_0065.Candidate]): iterator of candidates to add
        @param sid(unicode): transport stream id
        @param client: %(doc_client)s
        @param mode(str, None): 'tcp' or 'udp', or None to have no attribute
        @return (domish.Element): parent <transport> element where <candidate> elements must be added
        """
        proxy = next(
            (
                candidate
                for candidate in candidates
                if candidate.type == self._s5b.TYPE_PROXY
            ),
            None,
        )
        transport_elt = domish.Element((NS_JINGLE_S5B, "transport"))
        transport_elt["sid"] = sid
        if proxy is not None:
            transport_elt["dstaddr"] = session_hash
        if mode is not None:
            transport_elt["mode"] = "tcp"  # XXX: we only manage tcp for now

        for candidate in candidates:
            log.debug(u"Adding candidate: {}".format(candidate))
            candidate_elt = transport_elt.addElement("candidate", NS_JINGLE_S5B)
            if candidate.id is None:
                candidate.id = unicode(uuid.uuid4())
            candidate_elt["cid"] = candidate.id
            candidate_elt["host"] = candidate.host
            candidate_elt["jid"] = candidate.jid.full()
            candidate_elt["port"] = unicode(candidate.port)
            candidate_elt["priority"] = unicode(candidate.priority)
            candidate_elt["type"] = candidate.type
        return transport_elt

    @defer.inlineCallbacks
    def jingleSessionInit(self, client, session, content_name):
        content_data = session["contents"][content_name]
        transport_data = content_data["transport_data"]
        sid = transport_data["sid"] = unicode(uuid.uuid4())
        session_hash = transport_data["session_hash"] = self._s5b.getSessionHash(
            session[u"local_jid"], session["peer_jid"], sid
        )
        transport_data["peer_session_hash"] = self._s5b.getSessionHash(
            session["peer_jid"], session[u"local_jid"], sid
        )  # requester and target are inversed for peer candidates
        transport_data["stream_d"] = self._s5b.registerHash(client, session_hash, None)
        candidates = transport_data["candidates"] = yield self._s5b.getCandidates(
            client, session["local_jid"])
        mode = "tcp"  # XXX: we only manage tcp for now
        transport_elt = self._buildCandidates(
            session, candidates, sid, session_hash, client, mode
        )

        defer.returnValue(transport_elt)

    def _proxyActivatedCb(self, iq_result_elt, client, candidate, session, content_name):
        """Called when activation confirmation has been received from proxy

        cf XEP-0260 § 2.4
        """
        # now that the proxy is activated, we have to inform other peer
        iq_elt, transport_elt = self._j.buildAction(
            client, self._j.A_TRANSPORT_INFO, session, content_name
        )
        activated_elt = transport_elt.addElement("activated")
        activated_elt["cid"] = candidate.id
        iq_elt.send()

    def _proxyActivatedEb(self, stanza_error, client, candidate, session, content_name):
        """Called when activation error has been received from proxy

        cf XEP-0260 § 2.4
        """
        # TODO: fallback to IBB
        # now that the proxy is activated, we have to inform other peer
        iq_elt, transport_elt = self._j.buildAction(
            client, self._j.A_TRANSPORT_INFO, session, content_name
        )
        transport_elt.addElement("proxy-error")
        iq_elt.send()
        log.warning(
            u"Can't activate proxy, we need to fallback to IBB: {reason}".format(
                reason=stanza_error.value.condition
            )
        )
        self.doFallback(session, content_name, client)

    def _foundPeerCandidate(
        self, candidate, session, transport_data, content_name, client
    ):
        """Called when the best candidate from other peer is found

        @param candidate(XEP_0065.Candidate, None): selected candidate,
            or None if no candidate is accessible
        @param session(dict):  session data
        @param transport_data(dict): transport data
        @param content_name(unicode): name of the current content
        @param client(unicode): %(doc_client)s
        """

        transport_data["best_candidate"] = candidate
        # we need to disconnect all non selected candidates before removing them
        for c in transport_data["peer_candidates"]:
            if c is None or c is candidate:
                continue
            c.discard()
        del transport_data["peer_candidates"]
        iq_elt, transport_elt = self._j.buildAction(
            client, self._j.A_TRANSPORT_INFO, session, content_name
        )
        if candidate is None:
            log.warning(u"Can't connect to any peer candidate")
            candidate_elt = transport_elt.addElement("candidate-error")
        else:
            log.info(u"Found best peer candidate: {}".format(unicode(candidate)))
            candidate_elt = transport_elt.addElement("candidate-used")
            candidate_elt["cid"] = candidate.id
        iq_elt.send()  # TODO: check result stanza
        self._checkCandidates(session, content_name, transport_data, client)

    def _checkCandidates(self, session, content_name, transport_data, client):
        """Called when a candidate has been choosed

        if we have both candidates, we select one, or fallback to an other transport
        @param session(dict):  session data
        @param content_name(unicode): name of the current content
        @param transport_data(dict): transport data
        @param client(unicode): %(doc_client)s
        """
        content_data = session["contents"][content_name]
        try:
            best_candidate = transport_data["best_candidate"]
        except KeyError:
            # we have not our best candidate yet
            return
        try:
            peer_best_candidate = transport_data["peer_best_candidate"]
        except KeyError:
            # we have not peer best candidate yet
            return

        # at this point we have both candidates, it's time to choose one
        if best_candidate is None or peer_best_candidate is None:
            choosed_candidate = best_candidate or peer_best_candidate
        else:
            if best_candidate.priority == peer_best_candidate.priority:
                # same priority, we choose initiator one according to XEP-0260 §2.4 #4
                log.debug(
                    u"Candidates have same priority, we select the one choosed by initiator"
                )
                if session["initiator"] == session[u"local_jid"]:
                    choosed_candidate = best_candidate
                else:
                    choosed_candidate = peer_best_candidate
            else:
                choosed_candidate = max(
                    best_candidate, peer_best_candidate, key=lambda c: c.priority
                )

        if choosed_candidate is None:
            log.warning(u"Socks5 negociation failed, we need to fallback to IBB")
            self.doFallback(session, content_name, client)
        else:
            if choosed_candidate == peer_best_candidate:
                # peer_best_candidate was choosed from the candidates we have sent
                # so our_candidate is true if choosed_candidate is peer_best_candidate
                our_candidate = True
                # than also mean that best_candidate must be discarded !
                try:
                    best_candidate.discard()
                except AttributeError:  # but it can be None
                    pass
            else:
                our_candidate = False

            log.info(
                u"Socks5 negociation successful, {who} candidate will be used: {candidate}".format(
                    who=u"our" if our_candidate else u"other peer",
                    candidate=choosed_candidate,
                )
            )
            del transport_data["best_candidate"]
            del transport_data["peer_best_candidate"]

            if choosed_candidate.type == self._s5b.TYPE_PROXY:
                # the stream transfer need to wait for proxy activation
                # (see XEP-0260 § 2.4)
                if our_candidate:
                    d = self._s5b.connectCandidate(
                        client, choosed_candidate, transport_data["session_hash"]
                    )
                    d.addCallback(
                        lambda __: choosed_candidate.activate(
                            transport_data["sid"], session["peer_jid"], client
                        )
                    )
                    args = [client, choosed_candidate, session, content_name]
                    d.addCallbacks(
                        self._proxyActivatedCb, self._proxyActivatedEb, args, None, args
                    )
                else:
                    # this Deferred will be called when we'll receive activation confirmation from other peer
                    d = transport_data["activation_d"] = defer.Deferred()
            else:
                d = defer.succeed(None)

            if content_data["senders"] == session["role"]:
                # we can now start the stream transfer (or start it after proxy activation)
                d.addCallback(
                    lambda __: choosed_candidate.startTransfer(
                        transport_data["session_hash"]
                    )
                )
                d.addErrback(self._startEb, session, content_name, client)

    def _startEb(self, fail, session, content_name, client):
        """Called when it's not possible to start the transfer

        Will try to fallback to IBB
        """
        try:
            reason = unicode(fail.value)
        except AttributeError:
            reason = unicode(fail)
        log.warning(u"Cant start transfert, we'll try fallback method: {}".format(reason))
        self.doFallback(session, content_name, client)

    def _candidateInfo(
        self, candidate_elt, session, content_name, transport_data, client
    ):
        """Called when best candidate has been received from peer (or if none is working)

        @param candidate_elt(domish.Element): candidate-used or candidate-error element
            (see XEP-0260 §2.3)
        @param session(dict):  session data
        @param content_name(unicode): name of the current content
        @param transport_data(dict): transport data
        @param client(unicode): %(doc_client)s
        """
        if candidate_elt.name == "candidate-error":
            # candidate-error, no candidate worked
            transport_data["peer_best_candidate"] = None
        else:
            # candidate-used, one candidate was choosed
            try:
                cid = candidate_elt.attributes["cid"]
            except KeyError:
                log.warning(u"No cid found in <candidate-used>")
                raise exceptions.DataError
            try:
                candidate = (
                    c for c in transport_data["candidates"] if c.id == cid
                ).next()
            except StopIteration:
                log.warning(u"Given cid doesn't correspond to any known candidate !")
                raise exceptions.DataError  # TODO: send an error to other peer, and use better exception
            except KeyError:
                # a transport-info can also be intentionaly sent too early by other peer
                # but there is little probability
                log.error(
                    u'"candidates" key doesn\'t exists in transport_data, it should at this point'
                )
                raise exceptions.InternalError
            # at this point we have the candidate choosed by other peer
            transport_data["peer_best_candidate"] = candidate
            log.info(u"Other peer best candidate: {}".format(candidate))

        del transport_data["candidates"]
        self._checkCandidates(session, content_name, transport_data, client)

    def _proxyActivationInfo(
        self, proxy_elt, session, content_name, transport_data, client
    ):
        """Called when proxy has been activated (or has sent an error)

        @param proxy_elt(domish.Element): <activated/> or <proxy-error/> element
            (see XEP-0260 §2.4)
        @param session(dict):  session data
        @param content_name(unicode): name of the current content
        @param transport_data(dict): transport data
        @param client(unicode): %(doc_client)s
        """
        try:
            activation_d = transport_data.pop("activation_d")
        except KeyError:
            log.warning(u"Received unexpected transport-info for proxy activation")

        if proxy_elt.name == "activated":
            activation_d.callback(None)
        else:
            activation_d.errback(ProxyError())

    @defer.inlineCallbacks
    def jingleHandler(self, client, action, session, content_name, transport_elt):
        content_data = session["contents"][content_name]
        transport_data = content_data["transport_data"]

        if action in (self._j.A_ACCEPTED_ACK, self._j.A_PREPARE_RESPONDER):
            pass

        elif action == self._j.A_SESSION_ACCEPT:
            # initiator side, we select a candidate in the ones sent by responder
            assert "peer_candidates" not in transport_data
            transport_data["peer_candidates"] = self._parseCandidates(transport_elt)

        elif action == self._j.A_START:
            session_hash = transport_data["session_hash"]
            peer_candidates = transport_data["peer_candidates"]
            stream_object = content_data["stream_object"]
            self._s5b.associateStreamObject(client, session_hash, stream_object)
            stream_d = transport_data.pop("stream_d")
            stream_d.chainDeferred(content_data["finished_d"])
            peer_session_hash = transport_data["peer_session_hash"]
            d = self._s5b.getBestCandidate(
                client, peer_candidates, session_hash, peer_session_hash
            )
            d.addCallback(
                self._foundPeerCandidate, session, transport_data, content_name, client
            )

        elif action == self._j.A_SESSION_INITIATE:
            # responder side, we select a candidate in the ones sent by initiator
            # and we give our candidates
            assert "peer_candidates" not in transport_data
            sid = transport_data["sid"] = transport_elt["sid"]
            session_hash = transport_data["session_hash"] = self._s5b.getSessionHash(
                session["local_jid"], session["peer_jid"], sid
            )
            peer_session_hash = transport_data[
                "peer_session_hash"
            ] = self._s5b.getSessionHash(
                session["peer_jid"], session["local_jid"], sid
            )  # requester and target are inversed for peer candidates
            peer_candidates = transport_data["peer_candidates"] = self._parseCandidates(
                transport_elt
            )
            stream_object = content_data["stream_object"]
            stream_d = self._s5b.registerHash(client, session_hash, stream_object)
            stream_d.chainDeferred(content_data["finished_d"])
            d = self._s5b.getBestCandidate(
                client, peer_candidates, session_hash, peer_session_hash
            )
            d.addCallback(
                self._foundPeerCandidate, session, transport_data, content_name, client
            )
            candidates = yield self._s5b.getCandidates(client, session["local_jid"])
            # we remove duplicate candidates
            candidates = [
                candidate for candidate in candidates if candidate not in peer_candidates
            ]

            transport_data["candidates"] = candidates
            # we can now build a new <transport> element with our candidates
            transport_elt = self._buildCandidates(
                session, candidates, sid, session_hash, client
            )

        elif action == self._j.A_TRANSPORT_INFO:
            # transport-info can be about candidate or proxy activation
            candidate_elt = None

            for method, names in (
                (self._candidateInfo, ("candidate-used", "candidate-error")),
                (self._proxyActivationInfo, ("activated", "proxy-error")),
            ):
                for name in names:
                    try:
                        candidate_elt = transport_elt.elements(NS_JINGLE_S5B, name).next()
                    except StopIteration:
                        continue
                    else:
                        method(
                            candidate_elt, session, content_name, transport_data, client
                        )
                        break

            if candidate_elt is None:
                log.warning(
                    u"Unexpected transport element: {}".format(transport_elt.toXml())
                )
        elif action == self._j.A_DESTROY:
            # the transport is replaced (fallback ?), We need mainly to kill XEP-0065 session.
            # note that sid argument is not necessary for sessions created by this plugin
            self._s5b.killSession(None, transport_data["session_hash"], None, client)
        else:
            log.warning(u"FIXME: unmanaged action {}".format(action))

        defer.returnValue(transport_elt)

    def jingleTerminate(self, client, action, session, content_name, reason_elt):
        if reason_elt.decline:
            log.debug(u"Session declined, deleting S5B session")
            # we just need to clean the S5B session if it is declined
            content_data = session["contents"][content_name]
            transport_data = content_data["transport_data"]
            self._s5b.killSession(None, transport_data["session_hash"], None, client)

    def _doFallback(self, feature_checked, session, content_name, client):
        """Do the fallback, method called once feature is checked

         @param feature_checked(bool): True if other peer can do IBB
         """
        if not feature_checked:
            log.warning(
                u"Other peer can't manage jingle IBB, be have to terminate the session"
            )
            self._j.terminate(client, self._j.REASON_CONNECTIVITY_ERROR, session)
        else:
            self._j.transportReplace(
                client, self._jingle_ibb.NAMESPACE, session, content_name
            )

    def doFallback(self, session, content_name, client):
        """Fallback to IBB transport, used in last resort

        @param session(dict):  session data
        @param content_name(unicode): name of the current content
        @param client(unicode): %(doc_client)s
        """
        if session["role"] != self._j.ROLE_INITIATOR:
            # only initiator must do the fallback, see XEP-0260 §3
            return
        if self._jingle_ibb is None:
            log.warning(
                u"Jingle IBB (XEP-0261) plugin is not available, we have to close the session"
            )
            self._j.terminate(client, self._j.REASON_CONNECTIVITY_ERROR, session)
        else:
            d = self.host.hasFeature(
                client, self._jingle_ibb.NAMESPACE, session["peer_jid"]
            )
            d.addCallback(self._doFallback, session, content_name, client)
        return d


class XEP_0260_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_JINGLE_S5B)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Jingle (XEP-0166)
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
from sat.tools import xml_tools

log = getLogger(__name__)
from sat.core import exceptions
from twisted.words.protocols.jabber import jid
from twisted.internet import defer
from twisted.internet import reactor
from wokkel import disco, iwokkel
from twisted.words.protocols.jabber import error
from twisted.words.protocols.jabber import xmlstream
from twisted.python import failure
from collections import namedtuple
import uuid
import time

from zope.interface import implements


IQ_SET = '/iq[@type="set"]'
NS_JINGLE = "urn:xmpp:jingle:1"
NS_JINGLE_ERROR = "urn:xmpp:jingle:errors:1"
JINGLE_REQUEST = IQ_SET + '/jingle[@xmlns="' + NS_JINGLE + '"]'
STATE_PENDING = "PENDING"
STATE_ACTIVE = "ACTIVE"
STATE_ENDED = "ENDED"
CONFIRM_TXT = D_("{entity} want to start a jingle session with you, do you accept ?")

PLUGIN_INFO = {
    C.PI_NAME: "Jingle",
    C.PI_IMPORT_NAME: "XEP-0166",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0166"],
    C.PI_MAIN: "XEP_0166",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Jingle"""),
}


ApplicationData = namedtuple("ApplicationData", ("namespace", "handler"))
TransportData = namedtuple("TransportData", ("namespace", "handler", "priority"))


class XEP_0166(object):
    ROLE_INITIATOR = "initiator"
    ROLE_RESPONDER = "responder"
    TRANSPORT_DATAGRAM = "UDP"
    TRANSPORT_STREAMING = "TCP"
    REASON_SUCCESS = "success"
    REASON_DECLINE = "decline"
    REASON_FAILED_APPLICATION = "failed-application"
    REASON_FAILED_TRANSPORT = "failed-transport"
    REASON_CONNECTIVITY_ERROR = "connectivity-error"
    A_SESSION_INITIATE = "session-initiate"
    A_SESSION_ACCEPT = "session-accept"
    A_SESSION_TERMINATE = "session-terminate"
    A_SESSION_INFO = "session-info"
    A_TRANSPORT_REPLACE = "transport-replace"
    A_TRANSPORT_ACCEPT = "transport-accept"
    A_TRANSPORT_REJECT = "transport-reject"
    A_TRANSPORT_INFO = "transport-info"
    # non standard actions
    A_PREPARE_INITIATOR = "prepare-initiator"  # initiator must prepare tranfer
    A_PREPARE_RESPONDER = "prepare-responder"  # responder must prepare tranfer
    A_ACCEPTED_ACK = (
        "accepted-ack"
    )  # session accepted ack has been received from initiator
    A_START = "start"  # application can start
    A_DESTROY = (
        "destroy"
    )  # called when a transport is destroyed (e.g. because it is remplaced). Used to do cleaning operations

    def __init__(self, host):
        log.info(_("plugin Jingle initialization"))
        self.host = host
        self._applications = {}  # key: namespace, value: application data
        self._transports = {}  # key: namespace, value: transport data
        # we also keep transports by type, they are then sorted by priority
        self._type_transports = {
            XEP_0166.TRANSPORT_DATAGRAM: [],
            XEP_0166.TRANSPORT_STREAMING: [],
        }

    def profileConnected(self, client):
        client.jingle_sessions = {}  # key = sid, value = session_data

    def getHandler(self, client):
        return XEP_0166_handler(self)

    def _delSession(self, client, sid):
        try:
            del client.jingle_sessions[sid]
        except KeyError:
            log.debug(u"Jingle session id [{}] is unknown, nothing to delete".format(sid))
        else:
            log.debug(u"Jingle session id [{}] deleted".format(sid))

    ## helpers methods to build stanzas ##

    def _buildJingleElt(self, client, session, action):
        iq_elt = client.IQ("set")
        iq_elt["from"] = session['local_jid'].full()
        iq_elt["to"] = session["peer_jid"].full()
        jingle_elt = iq_elt.addElement("jingle", NS_JINGLE)
        jingle_elt["sid"] = session["id"]
        jingle_elt["action"] = action
        return iq_elt, jingle_elt

    def sendError(self, client, error_condition, sid, request, jingle_condition=None):
        """Send error stanza

        @param error_condition: one of twisted.words.protocols.jabber.error.STANZA_CONDITIONS keys
        @param sid(unicode,None): jingle session id, or None, if session must not be destroyed
        @param request(domish.Element): original request
        @param jingle_condition(None, unicode): if not None, additional jingle-specific error information
        """
        iq_elt = error.StanzaError(error_condition).toResponse(request)
        if jingle_condition is not None:
            iq_elt.error.addElement((NS_JINGLE_ERROR, jingle_condition))
        if error.STANZA_CONDITIONS[error_condition]["type"] == "cancel" and sid:
            self._delSession(client, sid)
            log.warning(
                u"Error while managing jingle session, cancelling: {condition}".format(
                    condition=error_condition
                )
            )
        client.send(iq_elt)

    def _terminateEb(self, failure_):
        log.warning(_(u"Error while terminating session: {msg}").format(msg=failure_))

    def terminate(self, client, reason, session):
        """Terminate the session

        send the session-terminate action, and delete the session data
        @param reason(unicode, list[domish.Element]): if unicode, will be transformed to an element
            if a list of element, add them as children of the <reason/> element
        @param session(dict): data of the session
        """
        iq_elt, jingle_elt = self._buildJingleElt(
            client, session, XEP_0166.A_SESSION_TERMINATE
        )
        reason_elt = jingle_elt.addElement("reason")
        if isinstance(reason, basestring):
            reason_elt.addElement(reason)
        else:
            for elt in reason:
                reason_elt.addChild(elt)
        self._delSession(client, session["id"])
        d = iq_elt.send()
        d.addErrback(self._terminateEb)
        return d

    ## errors which doesn't imply a stanza sending ##

    def _iqError(self, failure_, sid, client):
        """Called when we got an <iq/> error

        @param failure_(failure.Failure): the exceptions raised
        @param sid(unicode): jingle session id
        """
        log.warning(
            u"Error while sending jingle <iq/> stanza: {failure_}".format(
                failure_=failure_.value
            )
        )
        self._delSession(client, sid)

    def _jingleErrorCb(self, fail, sid, request, client):
        """Called when something is going wrong while parsing jingle request

        The error condition depend of the exceptions raised:
            exceptions.DataError raise a bad-request condition
        @param fail(failure.Failure): the exceptions raised
        @param sid(unicode): jingle session id
        @param request(domsih.Element): jingle request
        @param client: %(doc_client)s
        """
        log.warning("Error while processing jingle request")
        if isinstance(fail, exceptions.DataError):
            self.sendError(client, "bad-request", sid, request)
        else:
            log.error("Unmanaged jingle exception")
            self._delSession(client, sid)
            raise fail

    ## methods used by other plugins ##

    def registerApplication(self, namespace, handler):
        """Register an application plugin

        @param namespace(unicode): application namespace managed by the plugin
        @param handler(object): instance of a class which manage the application.
            May have the following methods:
                - requestConfirmation(session, desc_elt, client):
                    - if present, it is called on when session must be accepted.
                    - if it return True the session is accepted, else rejected.
                        A Deferred can be returned
                    - if not present, a generic accept dialog will be used
                - jingleSessionInit(client, self, session, content_name[, *args, **kwargs]): must return the domish.Element used for initial content
                - jingleHandler(client, self, action, session, content_name, transport_elt):
                    called on several action to negociate the application or transport
                - jingleTerminate: called on session terminate, with reason_elt
                    May be used to clean session
        """
        if namespace in self._applications:
            raise exceptions.ConflictError(
                u"Trying to register already registered namespace {}".format(namespace)
            )
        self._applications[namespace] = ApplicationData(
            namespace=namespace, handler=handler
        )
        log.debug(u"new jingle application registered")

    def registerTransport(self, namespace, transport_type, handler, priority=0):
        """Register a transport plugin

        @param namespace(unicode): the XML namespace used for this transport
        @param transport_type(unicode): type of transport to use (see XEP-0166 §8)
        @param handler(object): instance of a class which manage the application.
            Must have the following methods:
                - jingleSessionInit(client, self, session, content_name[, *args, **kwargs]): must return the domish.Element used for initial content
                - jingleHandler(client, self, action, session, content_name, transport_elt):
                    called on several action to negociate the application or transport
        @param priority(int): priority of this transport
        """
        assert transport_type in (
            XEP_0166.TRANSPORT_DATAGRAM,
            XEP_0166.TRANSPORT_STREAMING,
        )
        if namespace in self._transports:
            raise exceptions.ConflictError(
                u"Trying to register already registered namespace {}".format(namespace)
            )
        transport_data = TransportData(
            namespace=namespace, handler=handler, priority=priority
        )
        self._type_transports[transport_type].append(transport_data)
        self._type_transports[transport_type].sort(
            key=lambda transport_data: transport_data.priority, reverse=True
        )
        self._transports[namespace] = transport_data
        log.debug(u"new jingle transport registered")

    @defer.inlineCallbacks
    def transportReplace(self, client, transport_ns, session, content_name):
        """Replace a transport

        @param transport_ns(unicode): namespace of the new transport to use
        @param session(dict): jingle session data
        @param content_name(unicode): name of the content
        """
        # XXX: for now we replace the transport before receiving confirmation from other peer
        #      this is acceptable because we terminate the session if transport is rejected.
        #      this behavious may change in the future.
        content_data = session["contents"][content_name]
        transport_data = content_data["transport_data"]
        try:
            transport = self._transports[transport_ns]
        except KeyError:
            raise exceptions.InternalError(u"Unkown transport")
        yield content_data["transport"].handler.jingleHandler(
            client, XEP_0166.A_DESTROY, session, content_name, None
        )
        content_data["transport"] = transport
        transport_data.clear()

        iq_elt, jingle_elt = self._buildJingleElt(
            client, session, XEP_0166.A_TRANSPORT_REPLACE
        )
        content_elt = jingle_elt.addElement("content")
        content_elt["name"] = content_name
        content_elt["creator"] = content_data["creator"]

        transport_elt = transport.handler.jingleSessionInit(client, session, content_name)
        content_elt.addChild(transport_elt)
        iq_elt.send()

    def buildAction(self, client, action, session, content_name):
        """Build an element according to requested action

        @param action(unicode): a jingle action (see XEP-0166 §7.2),
            session-* actions are not managed here
            transport-replace is managed in the dedicated [transportReplace] method
        @param session(dict): jingle session data
        @param content_name(unicode): name of the content
        @return (tuple[domish.Element, domish.Element]): parent <iq> element, <transport> or <description> element, according to action
        """
        # we first build iq, jingle and content element which are the same in every cases
        iq_elt, jingle_elt = self._buildJingleElt(client, session, action)
        # FIXME: XEP-0260 § 2.3 Ex 5 has an initiator attribute, but it should not according to XEP-0166 §7.1 table 1, must be checked
        content_data = session["contents"][content_name]
        content_elt = jingle_elt.addElement("content")
        content_elt["name"] = content_name
        content_elt["creator"] = content_data["creator"]

        if action == XEP_0166.A_TRANSPORT_INFO:
            context_elt = transport_elt = content_elt.addElement(
                "transport", content_data["transport"].namespace
            )
            transport_elt["sid"] = content_data["transport_data"]["sid"]
        else:
            raise exceptions.InternalError(u"unmanaged action {}".format(action))

        return iq_elt, context_elt

    def buildSessionInfo(self, client, session):
        """Build a session-info action

        @param session(dict): jingle session data
        @return (tuple[domish.Element, domish.Element]): parent <iq> element, <jingle> element
        """
        return self._buildJingleElt(client, session, XEP_0166.A_SESSION_INFO)

    @defer.inlineCallbacks
    def initiate(self, client, peer_jid, contents):
        """Send a session initiation request

        @param peer_jid(jid.JID): jid to establith session with
        @param contents(list[dict]): list of contents to use:
            The dict must have the following keys:
                - app_ns(unicode): namespace of the application
            the following keys are optional:
                - transport_type(unicode): type of transport to use (see XEP-0166 §8)
                    default to TRANSPORT_STREAMING
                - name(unicode): name of the content
                - senders(unicode): One of XEP_0166.ROLE_INITIATOR, XEP_0166.ROLE_RESPONDER, both or none
                    default to BOTH (see XEP-0166 §7.3)
                - app_args(list): args to pass to the application plugin
                - app_kwargs(dict): keyword args to pass to the application plugin
        @return D(unicode): jingle session id
        """
        assert contents  # there must be at least one content
        if (peer_jid == client.jid
            or client.is_component and peer_jid.host == client.jid.host):
            raise ValueError(_(u"You can't do a jingle session with yourself"))
        initiator = client.jid
        sid = unicode(uuid.uuid4())
        # TODO: session cleaning after timeout ?
        session = client.jingle_sessions[sid] = {
            "id": sid,
            "state": STATE_PENDING,
            "initiator": initiator,
            "role": XEP_0166.ROLE_INITIATOR,
            "local_jid": client.jid,
            "peer_jid": peer_jid,
            "started": time.time(),
            "contents": {},
        }
        iq_elt, jingle_elt = self._buildJingleElt(
            client, session, XEP_0166.A_SESSION_INITIATE
        )
        jingle_elt["initiator"] = initiator.full()

        contents_dict = session["contents"]

        for content in contents:
            # we get the application plugin
            app_ns = content["app_ns"]
            try:
                application = self._applications[app_ns]
            except KeyError:
                raise exceptions.InternalError(
                    u"No application registered for {}".format(app_ns)
                )

            # and the transport plugin
            transport_type = content.get("transport_type", XEP_0166.TRANSPORT_STREAMING)
            try:
                transport = self._type_transports[transport_type][0]
            except IndexError:
                raise exceptions.InternalError(
                    u"No transport registered for {}".format(transport_type)
                )

            # we build the session data
            content_data = {
                "application": application,
                "application_data": {},
                "transport": transport,
                "transport_data": {},
                "creator": XEP_0166.ROLE_INITIATOR,
                "senders": content.get("senders", "both"),
            }
            try:
                content_name = content["name"]
            except KeyError:
                content_name = unicode(uuid.uuid4())
            else:
                if content_name in contents_dict:
                    raise exceptions.InternalError(
                        "There is already a content with this name"
                    )
            contents_dict[content_name] = content_data

            # we construct the content element
            content_elt = jingle_elt.addElement("content")
            content_elt["creator"] = content_data["creator"]
            content_elt["name"] = content_name
            try:
                content_elt["senders"] = content["senders"]
            except KeyError:
                pass

            # then the description element
            app_args = content.get("app_args", [])
            app_kwargs = content.get("app_kwargs", {})
            desc_elt = yield application.handler.jingleSessionInit(
                client, session, content_name, *app_args, **app_kwargs
            )
            content_elt.addChild(desc_elt)

            # and the transport one
            transport_elt = yield transport.handler.jingleSessionInit(
                client, session, content_name
            )
            content_elt.addChild(transport_elt)

        try:
            yield iq_elt.send()
        except Exception as e:
            failure_ = failure.Failure(e)
            self._iqError(failure_, sid, client)
            raise failure_

    def delayedContentTerminate(self, *args, **kwargs):
        """Put contentTerminate in queue but don't execute immediately

        This is used to terminate a content inside a handler, to avoid modifying contents
        """
        reactor.callLater(0, self.contentTerminate, *args, **kwargs)

    def contentTerminate(self, client, session, content_name, reason=REASON_SUCCESS):
        """Terminate and remove a content

        if there is no more content, then session is terminated
        @param session(dict): jingle session
        @param content_name(unicode): name of the content terminated
        @param reason(unicode): reason of the termination
        """
        contents = session["contents"]
        del contents[content_name]
        if not contents:
            self.terminate(client, reason, session)

    ## defaults methods called when plugin doesn't have them ##

    def jingleRequestConfirmationDefault(
        self, client, action, session, content_name, desc_elt
    ):
        """This method request confirmation for a jingle session"""
        log.debug(u"Using generic jingle confirmation method")
        return xml_tools.deferConfirm(
            self.host,
            _(CONFIRM_TXT).format(entity=session["peer_jid"].full()),
            _("Confirm Jingle session"),
            profile=client.profile,
        )

    ## jingle events ##

    def _onJingleRequest(self, request, client):
        """Called when any jingle request is received

        The request will then be dispatched to appropriate method
        according to current state
        @param request(domish.Element): received IQ request
        """
        request.handled = True
        jingle_elt = request.elements(NS_JINGLE, "jingle").next()

        # first we need the session id
        try:
            sid = jingle_elt["sid"]
            if not sid:
                raise KeyError
        except KeyError:
            log.warning(u"Received jingle request has no sid attribute")
            self.sendError(client, "bad-request", None, request)
            return

        # then the action
        try:
            action = jingle_elt["action"]
            if not action:
                raise KeyError
        except KeyError:
            log.warning(u"Received jingle request has no action")
            self.sendError(client, "bad-request", None, request)
            return

        peer_jid = jid.JID(request["from"])

        # we get or create the session
        try:
            session = client.jingle_sessions[sid]
        except KeyError:
            if action == XEP_0166.A_SESSION_INITIATE:
                pass
            elif action == XEP_0166.A_SESSION_TERMINATE:
                log.debug(
                    u"ignoring session terminate action (inexisting session id): {request_id} [{profile}]".format(
                        request_id=sid, profile=client.profile
                    )
                )
                return
            else:
                log.warning(
                    u"Received request for an unknown session id: {request_id} [{profile}]".format(
                        request_id=sid, profile=client.profile
                    )
                )
                self.sendError(client, "item-not-found", None, request, "unknown-session")
                return

            session = client.jingle_sessions[sid] = {
                "id": sid,
                "state": STATE_PENDING,
                "initiator": peer_jid,
                "role": XEP_0166.ROLE_RESPONDER,
                # we store local_jid using request['to'] because for a component the jid
                # used may not be client.jid (if a local part is used).
                "local_jid": jid.JID(request['to']),
                "peer_jid": peer_jid,
                "started": time.time(),
            }
        else:
            if session["peer_jid"] != peer_jid:
                log.warning(
                    u"sid conflict ({}), the jid doesn't match. Can be a collision, a hack attempt, or a bad sid generation".format(
                        sid
                    )
                )
                self.sendError(client, "service-unavailable", sid, request)
                return
            if session["id"] != sid:
                log.error(u"session id doesn't match")
                self.sendError(client, "service-unavailable", sid, request)
                raise exceptions.InternalError

        if action == XEP_0166.A_SESSION_INITIATE:
            self.onSessionInitiate(client, request, jingle_elt, session)
        elif action == XEP_0166.A_SESSION_TERMINATE:
            self.onSessionTerminate(client, request, jingle_elt, session)
        elif action == XEP_0166.A_SESSION_ACCEPT:
            self.onSessionAccept(client, request, jingle_elt, session)
        elif action == XEP_0166.A_SESSION_INFO:
            self.onSessionInfo(client, request, jingle_elt, session)
        elif action == XEP_0166.A_TRANSPORT_INFO:
            self.onTransportInfo(client, request, jingle_elt, session)
        elif action == XEP_0166.A_TRANSPORT_REPLACE:
            self.onTransportReplace(client, request, jingle_elt, session)
        elif action == XEP_0166.A_TRANSPORT_ACCEPT:
            self.onTransportAccept(client, request, jingle_elt, session)
        elif action == XEP_0166.A_TRANSPORT_REJECT:
            self.onTransportReject(client, request, jingle_elt, session)
        else:
            raise exceptions.InternalError(u"Unknown action {}".format(action))

    ## Actions callbacks ##

    def _parseElements(
        self,
        jingle_elt,
        session,
        request,
        client,
        new=False,
        creator=ROLE_INITIATOR,
        with_application=True,
        with_transport=True,
    ):
        """Parse contents elements and fill contents_dict accordingly

        after the parsing, contents_dict will containt handlers, "desc_elt" and "transport_elt"
        @param jingle_elt(domish.Element): parent <jingle> element, containing one or more <content>
        @param session(dict): session data
        @param request(domish.Element): the whole request
        @param client: %(doc_client)s
        @param new(bool): True if the content is new and must be created,
            else the content must exists, and session data will be filled
        @param creator(unicode): only used if new is True: creating pear (see § 7.3)
        @param with_application(bool): if True, raise an error if there is no <description> element else ignore it
        @param with_transport(bool): if True, raise an error if there is no <transport> element else ignore it
        @raise exceptions.CancelError: the error is treated and the calling method can cancel the treatment (i.e. return)
        """
        contents_dict = session["contents"]
        content_elts = jingle_elt.elements(NS_JINGLE, "content")

        for content_elt in content_elts:
            name = content_elt["name"]

            if new:
                # the content must not exist, we check it
                if not name or name in contents_dict:
                    self.sendError(client, "bad-request", session["id"], request)
                    raise exceptions.CancelError
                content_data = contents_dict[name] = {
                    "creator": creator,
                    "senders": content_elt.attributes.get("senders", "both"),
                }
            else:
                # the content must exist, we check it
                try:
                    content_data = contents_dict[name]
                except KeyError:
                    log.warning(u"Other peer try to access an unknown content")
                    self.sendError(client, "bad-request", session["id"], request)
                    raise exceptions.CancelError

            # application
            if with_application:
                desc_elt = content_elt.description
                if not desc_elt:
                    self.sendError(client, "bad-request", session["id"], request)
                    raise exceptions.CancelError

                if new:
                    # the content is new, we need to check and link the application
                    app_ns = desc_elt.uri
                    if not app_ns or app_ns == NS_JINGLE:
                        self.sendError(client, "bad-request", session["id"], request)
                        raise exceptions.CancelError

                    try:
                        application = self._applications[app_ns]
                    except KeyError:
                        log.warning(
                            u"Unmanaged application namespace [{}]".format(app_ns)
                        )
                        self.sendError(
                            client, "service-unavailable", session["id"], request
                        )
                        raise exceptions.CancelError

                    content_data["application"] = application
                    content_data["application_data"] = {}
                else:
                    # the content exists, we check that we have not a former desc_elt
                    if "desc_elt" in content_data:
                        raise exceptions.InternalError(
                            u"desc_elt should not exist at this point"
                        )

                content_data["desc_elt"] = desc_elt

            # transport
            if with_transport:
                transport_elt = content_elt.transport
                if not transport_elt:
                    self.sendError(client, "bad-request", session["id"], request)
                    raise exceptions.CancelError

                if new:
                    # the content is new, we need to check and link the transport
                    transport_ns = transport_elt.uri
                    if not app_ns or app_ns == NS_JINGLE:
                        self.sendError(client, "bad-request", session["id"], request)
                        raise exceptions.CancelError

                    try:
                        transport = self._transports[transport_ns]
                    except KeyError:
                        raise exceptions.InternalError(
                            u"No transport registered for namespace {}".format(
                                transport_ns
                            )
                        )
                    content_data["transport"] = transport
                    content_data["transport_data"] = {}
                else:
                    # the content exists, we check that we have not a former transport_elt
                    if "transport_elt" in content_data:
                        raise exceptions.InternalError(
                            u"transport_elt should not exist at this point"
                        )

                content_data["transport_elt"] = transport_elt

    def _ignore(self, client, action, session, content_name, elt):
        """Dummy method used when not exception must be raised if a method is not implemented in _callPlugins

        must be used as app_default_cb and/or transp_default_cb
        """
        return elt

    def _callPlugins(
        self,
        client,
        action,
        session,
        app_method_name="jingleHandler",
        transp_method_name="jingleHandler",
        app_default_cb=None,
        transp_default_cb=None,
        delete=True,
        elements=True,
        force_element=None,
    ):
        """Call application and transport plugin methods for all contents

        @param action(unicode): jingle action name
        @param session(dict): jingle session data
        @param app_method_name(unicode, None): name of the method to call for applications
            None to ignore
        @param transp_method_name(unicode, None): name of the method to call for transports
            None to ignore
        @param app_default_cb(callable, None): default callback to use if plugin has not app_method_name
            None to raise an exception instead
        @param transp_default_cb(callable, None): default callback to use if plugin has not transp_method_name
            None to raise an exception instead
        @param delete(bool): if True, remove desc_elt and transport_elt from session
            ignored if elements is False
        @param elements(bool): True if elements(desc_elt and tranport_elt) must be managed
            must be True if _callPlugins is used in a request, and False if it used after a request
            (i.e. on <iq> result or error)
        @param force_element(None, domish.Element, object): if elements is False, it is used as element parameter
            else it is ignored
        @return (list[defer.Deferred]): list of launched Deferred
        @raise exceptions.NotFound: method is not implemented
        """
        contents_dict = session["contents"]
        defers_list = []
        for content_name, content_data in contents_dict.iteritems():
            for method_name, handler_key, default_cb, elt_name in (
                (app_method_name, "application", app_default_cb, "desc_elt"),
                (transp_method_name, "transport", transp_default_cb, "transport_elt"),
            ):
                if method_name is None:
                    continue

                handler = content_data[handler_key].handler
                try:
                    method = getattr(handler, method_name)
                except AttributeError:
                    if default_cb is None:
                        raise exceptions.NotFound(
                            u"{} not implemented !".format(method_name)
                        )
                    else:
                        method = default_cb
                if elements:
                    elt = content_data.pop(elt_name) if delete else content_data[elt_name]
                else:
                    elt = force_element
                d = defer.maybeDeferred(
                    method, client, action, session, content_name, elt
                )
                defers_list.append(d)

        return defers_list

    def onSessionInitiate(self, client, request, jingle_elt, session):
        """Called on session-initiate action

        The "jingleRequestConfirmation" method of each application will be called
        (or self.jingleRequestConfirmationDefault if the former doesn't exist).
        The session is only accepted if all application are confirmed.
        The application must manage itself multiple contents scenari (e.g. audio/video).
        @param client: %(doc_client)s
        @param request(domish.Element): full request
        @param jingle_elt(domish.Element): <jingle> element
        @param session(dict): session data
        """
        if "contents" in session:
            raise exceptions.InternalError(
                "Contents dict should not already exist at this point"
            )
        session["contents"] = contents_dict = {}

        try:
            self._parseElements(
                jingle_elt, session, request, client, True, XEP_0166.ROLE_INITIATOR
            )
        except exceptions.CancelError:
            return

        if not contents_dict:
            # there MUST be at least one content
            self.sendError(client, "bad-request", session["id"], request)
            return

        # at this point we can send the <iq/> result to confirm reception of the request
        client.send(xmlstream.toResponse(request, "result"))

        # we now request each application plugin confirmation
        # and if all are accepted, we can accept the session
        confirm_defers = self._callPlugins(
            client,
            XEP_0166.A_SESSION_INITIATE,
            session,
            "jingleRequestConfirmation",
            None,
            self.jingleRequestConfirmationDefault,
            delete=False,
        )

        confirm_dlist = defer.gatherResults(confirm_defers)
        confirm_dlist.addCallback(self._confirmationCb, session, jingle_elt, client)
        confirm_dlist.addErrback(self._jingleErrorCb, session["id"], request, client)

    def _confirmationCb(self, confirm_results, session, jingle_elt, client):
        """Method called when confirmation from user has been received

        This method is only called for the responder
        @param confirm_results(list[bool]): all True if session is accepted
        @param session(dict): session data
        @param jingle_elt(domish.Element): jingle data of this session
        @param client: %(doc_client)s
        """
        confirmed = all(confirm_results)
        if not confirmed:
            return self.terminate(client, XEP_0166.REASON_DECLINE, session)

        iq_elt, jingle_elt = self._buildJingleElt(
            client, session, XEP_0166.A_SESSION_ACCEPT
        )
        jingle_elt["responder"] = session['local_jid'].full()

        # contents

        def addElement(domish_elt, content_elt):
            content_elt.addChild(domish_elt)

        defers_list = []

        for content_name, content_data in session["contents"].iteritems():
            content_elt = jingle_elt.addElement("content")
            content_elt["creator"] = XEP_0166.ROLE_INITIATOR
            content_elt["name"] = content_name

            application = content_data["application"]
            app_session_accept_cb = application.handler.jingleHandler

            app_d = defer.maybeDeferred(
                app_session_accept_cb,
                client,
                XEP_0166.A_SESSION_INITIATE,
                session,
                content_name,
                content_data.pop("desc_elt"),
            )
            app_d.addCallback(addElement, content_elt)
            defers_list.append(app_d)

            transport = content_data["transport"]
            transport_session_accept_cb = transport.handler.jingleHandler

            transport_d = defer.maybeDeferred(
                transport_session_accept_cb,
                client,
                XEP_0166.A_SESSION_INITIATE,
                session,
                content_name,
                content_data.pop("transport_elt"),
            )
            transport_d.addCallback(addElement, content_elt)
            defers_list.append(transport_d)

        d_list = defer.DeferredList(defers_list)
        d_list.addCallback(
            lambda __: self._callPlugins(
                client,
                XEP_0166.A_PREPARE_RESPONDER,
                session,
                app_method_name=None,
                elements=False,
            )
        )
        d_list.addCallback(lambda __: iq_elt.send())

        def changeState(__, session):
            session["state"] = STATE_ACTIVE

        d_list.addCallback(changeState, session)
        d_list.addCallback(
            lambda __: self._callPlugins(
                client, XEP_0166.A_ACCEPTED_ACK, session, elements=False
            )
        )
        d_list.addErrback(self._iqError, session["id"], client)
        return d_list

    def onSessionTerminate(self, client, request, jingle_elt, session):
        # TODO: check reason, display a message to user if needed
        log.debug("Jingle Session {} terminated".format(session["id"]))
        try:
            reason_elt = jingle_elt.elements(NS_JINGLE, "reason").next()
        except StopIteration:
            log.warning(u"No reason given for session termination")
            reason_elt = jingle_elt.addElement("reason")

        terminate_defers = self._callPlugins(
            client,
            XEP_0166.A_SESSION_TERMINATE,
            session,
            "jingleTerminate",
            "jingleTerminate",
            self._ignore,
            self._ignore,
            elements=False,
            force_element=reason_elt,
        )
        terminate_dlist = defer.DeferredList(terminate_defers)

        terminate_dlist.addCallback(lambda __: self._delSession(client, session["id"]))
        client.send(xmlstream.toResponse(request, "result"))

    def onSessionAccept(self, client, request, jingle_elt, session):
        """Method called once session is accepted

        This method is only called for initiator
        @param client: %(doc_client)s
        @param request(domish.Element): full <iq> request
        @param jingle_elt(domish.Element): the <jingle> element
        @param session(dict): session data
        """
        log.debug(u"Jingle session {} has been accepted".format(session["id"]))

        try:
            self._parseElements(jingle_elt, session, request, client)
        except exceptions.CancelError:
            return

        # at this point we can send the <iq/> result to confirm reception of the request
        client.send(xmlstream.toResponse(request, "result"))
        # and change the state
        session["state"] = STATE_ACTIVE

        negociate_defers = []
        negociate_defers = self._callPlugins(client, XEP_0166.A_SESSION_ACCEPT, session)

        negociate_dlist = defer.DeferredList(negociate_defers)

        # after negociations we start the transfer
        negociate_dlist.addCallback(
            lambda __: self._callPlugins(
                client, XEP_0166.A_START, session, app_method_name=None, elements=False
            )
        )

    def _onSessionCb(self, result, client, request, jingle_elt, session):
        client.send(xmlstream.toResponse(request, "result"))

    def _onSessionEb(self, failure_, client, request, jingle_elt, session):
        log.error(u"Error while handling onSessionInfo: {}".format(failure_.value))
        # XXX: only error managed so far, maybe some applications/transports need more
        self.sendError(
            client, "feature-not-implemented", None, request, "unsupported-info"
        )

    def onSessionInfo(self, client, request, jingle_elt, session):
        """Method called when a session-info action is received from other peer

        This method is only called for initiator
        @param client: %(doc_client)s
        @param request(domish.Element): full <iq> request
        @param jingle_elt(domish.Element): the <jingle> element
        @param session(dict): session data
        """
        if not jingle_elt.children:
            # this is a session ping, see XEP-0166 §6.8
            client.send(xmlstream.toResponse(request, "result"))
            return

        try:
            # XXX: session-info is most likely only used for application, so we don't call transport plugins
            #      if a future transport use it, this behaviour must be adapted
            defers = self._callPlugins(
                client,
                XEP_0166.A_SESSION_INFO,
                session,
                "jingleSessionInfo",
                None,
                elements=False,
                force_element=jingle_elt,
            )
        except exceptions.NotFound as e:
            self._onSessionEb(failure.Failure(e), client, request, jingle_elt, session)
            return

        dlist = defer.DeferredList(defers, fireOnOneErrback=True)
        dlist.addCallback(self._onSessionCb, client, request, jingle_elt, session)
        dlist.addErrback(self._onSessionCb, client, request, jingle_elt, session)

    @defer.inlineCallbacks
    def onTransportReplace(self, client, request, jingle_elt, session):
        """A transport change is requested

        The request is parsed, and jingleHandler is called on concerned transport plugin(s)
        @param client: %(doc_client)s
        @param request(domish.Element): full <iq> request
        @param jingle_elt(domish.Element): the <jingle> element
        @param session(dict): session data
        """
        log.debug(u"Other peer wants to replace the transport")
        try:
            self._parseElements(
                jingle_elt, session, request, client, with_application=False
            )
        except exceptions.CancelError:
            defer.returnValue(None)

        client.send(xmlstream.toResponse(request, "result"))

        content_name = None
        to_replace = []

        for content_name, content_data in session["contents"].iteritems():
            try:
                transport_elt = content_data.pop("transport_elt")
            except KeyError:
                continue
            transport_ns = transport_elt.uri
            try:
                transport = self._transports[transport_ns]
            except KeyError:
                log.warning(
                    u"Other peer want to replace current transport with an unknown one: {}".format(
                        transport_ns
                    )
                )
                content_name = None
                break
            to_replace.append((content_name, content_data, transport, transport_elt))

        if content_name is None:
            # wa can't accept the replacement
            iq_elt, reject_jingle_elt = self._buildJingleElt(
                client, session, XEP_0166.A_TRANSPORT_REJECT
            )
            for child in jingle_elt.children:
                reject_jingle_elt.addChild(child)

            iq_elt.send()
            defer.returnValue(None)

        # at this point, everything is alright and we can replace the transport(s)
        # this is similar to an session-accept action, but for transports only
        iq_elt, accept_jingle_elt = self._buildJingleElt(
            client, session, XEP_0166.A_TRANSPORT_ACCEPT
        )
        for content_name, content_data, transport, transport_elt in to_replace:
            # we can now actually replace the transport
            yield content_data["transport"].handler.jingleHandler(
                client, XEP_0166.A_DESTROY, session, content_name, None
            )
            content_data["transport"] = transport
            content_data["transport_data"].clear()
            # and build the element
            content_elt = accept_jingle_elt.addElement("content")
            content_elt["name"] = content_name
            content_elt["creator"] = content_data["creator"]
            # we notify the transport and insert its <transport/> in the answer
            accept_transport_elt = yield transport.handler.jingleHandler(
                client, XEP_0166.A_TRANSPORT_REPLACE, session, content_name, transport_elt
            )
            content_elt.addChild(accept_transport_elt)
            # there is no confirmation needed here, so we can directly prepare it
            yield transport.handler.jingleHandler(
                client, XEP_0166.A_PREPARE_RESPONDER, session, content_name, None
            )

        iq_elt.send()

    def onTransportAccept(self, client, request, jingle_elt, session):
        """Method called once transport replacement is accepted

        @param client: %(doc_client)s
        @param request(domish.Element): full <iq> request
        @param jingle_elt(domish.Element): the <jingle> element
        @param session(dict): session data
        """
        log.debug(u"new transport has been accepted")

        try:
            self._parseElements(
                jingle_elt, session, request, client, with_application=False
            )
        except exceptions.CancelError:
            return

        # at this point we can send the <iq/> result to confirm reception of the request
        client.send(xmlstream.toResponse(request, "result"))

        negociate_defers = []
        negociate_defers = self._callPlugins(
            client, XEP_0166.A_TRANSPORT_ACCEPT, session, app_method_name=None
        )

        negociate_dlist = defer.DeferredList(negociate_defers)

        # after negociations we start the transfer
        negociate_dlist.addCallback(
            lambda __: self._callPlugins(
                client, XEP_0166.A_START, session, app_method_name=None, elements=False
            )
        )

    def onTransportReject(self, client, request, jingle_elt, session):
        """Method called when a transport replacement is refused

        @param client: %(doc_client)s
        @param request(domish.Element): full <iq> request
        @param jingle_elt(domish.Element): the <jingle> element
        @param session(dict): session data
        """
        # XXX: for now, we terminate the session in case of transport-reject
        #      this behaviour may change in the future
        self.terminate(client, "failed-transport", session)

    def onTransportInfo(self, client, request, jingle_elt, session):
        """Method called when a transport-info action is received from other peer

        The request is parsed, and jingleHandler is called on concerned transport plugin(s)
        @param client: %(doc_client)s
        @param request(domish.Element): full <iq> request
        @param jingle_elt(domish.Element): the <jingle> element
        @param session(dict): session data
        """
        log.debug(u"Jingle session {} has been accepted".format(session["id"]))

        try:
            self._parseElements(
                jingle_elt, session, request, client, with_application=False
            )
        except exceptions.CancelError:
            return

        # The parsing was OK, we send the <iq> result
        client.send(xmlstream.toResponse(request, "result"))

        for content_name, content_data in session["contents"].iteritems():
            try:
                transport_elt = content_data.pop("transport_elt")
            except KeyError:
                continue
            else:
                content_data["transport"].handler.jingleHandler(
                    client,
                    XEP_0166.A_TRANSPORT_INFO,
                    session,
                    content_name,
                    transport_elt,
                )


class XEP_0166_handler(xmlstream.XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            JINGLE_REQUEST, self.plugin_parent._onJingleRequest, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_JINGLE)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

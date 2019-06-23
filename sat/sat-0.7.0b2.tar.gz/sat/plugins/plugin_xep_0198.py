#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing raw XML log
# Copyright (C) 2011  Jérôme Poisson (goffi@goffi.org)

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
from twisted.words.protocols.jabber import client as jabber_client
from twisted.words.protocols.jabber import xmlstream
from twisted.words.xish import domish
from twisted.internet import defer
from twisted.internet import task, reactor
from functools import partial
from wokkel import disco, iwokkel
from zope.interface import implements
import collections
import time

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: "Stream Management",
    C.PI_IMPORT_NAME: "XEP-0198",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0198"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0198",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(u"""Implementation of Stream Management"""),
}

NS_SM = u"urn:xmpp:sm:3"
SM_ENABLED = '/enabled[@xmlns="' + NS_SM + '"]'
SM_RESUMED = '/resumed[@xmlns="' + NS_SM + '"]'
SM_FAILED = '/failed[@xmlns="' + NS_SM + '"]'
SM_R_REQUEST = '/r[@xmlns="' + NS_SM + '"]'
SM_A_REQUEST = '/a[@xmlns="' + NS_SM + '"]'
SM_H_REQUEST = '/h[@xmlns="' + NS_SM + '"]'
# Max number of stanza to send before requesting ack
MAX_STANZA_ACK_R = 5
# Max number of seconds before requesting ack
MAX_DELAY_ACK_R = 30
MAX_COUNTER = 2**32
RESUME_MAX = 5*60
# if we don't have an answer to ACK REQUEST after this delay, connection is aborted
ACK_TIMEOUT = 35


class ProfileSessionData(object):
    out_counter = 0
    in_counter = 0
    session_id = None
    location = None
    session_max = None
    # True when an ack answer is expected
    ack_requested = False
    last_ack_r = 0
    disconnected_time = None

    def __init__(self, callback, **kw):
        self.buffer = collections.deque()
        self.buffer_idx = 0
        self._enabled = False
        self.timer = None
        # time used when doing a ack request
        # when it times out, connection is aborted
        self.req_timer = None
        self.callback_data = (callback, kw)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        if enabled:
            if self._enabled:
                raise exceptions.InternalError(
                    u"Stream Management can't be enabled twice")
            self._enabled = True
            callback, kw = self.callback_data
            self.timer = task.LoopingCall(callback, **kw)
            self.timer.start(MAX_DELAY_ACK_R, now=False)
        else:
            self._enabled = False
            if self.timer is not None:
                self.timer.stop()
                self.timer = None

    @property
    def resume_enabled(self):
        return self.session_id is not None

    def reset(self):
        self.enabled = False
        self.buffer.clear()
        self.buffer_idx = 0
        self.in_counter = self.out_counter = 0
        self.session_id = self.location = None
        self.ack_requested = False
        self.last_ack_r = 0
        if self.req_timer is not None:
            if self.req_timer.active():
                log.error(u"req_timer has been called/cancelled but not reset")
            else:
                self.req_timer.cancel()
            self.req_timer = None


class XEP_0198(object):
    # FIXME: location is not handled yet

    def __init__(self, host):
        log.info(_("Plugin Stream Management initialization"))
        self.host = host
        host.registerNamespace(u'sm', NS_SM)
        host.trigger.add("stream_hooks", self.addHooks)
        host.trigger.add("xml_init", self._XMLInitTrigger)
        host.trigger.add("disconnecting", self._disconnectingTrigger)
        host.trigger.add("disconnected", self._disconnectedTrigger)
        try:
            self._ack_timeout = int(host.memory.getConfig("", "ack_timeout", ACK_TIMEOUT))
        except ValueError:
            log.error(_(u"Invalid ack_timeout value, please check your configuration"))
            self._ack_timeout = ACK_TIMEOUT
        if not self._ack_timeout:
            log.info(_(u"Ack timeout disabled"))
        else:
            log.info(_(u"Ack timeout set to {timeout}s").format(
                timeout=self._ack_timeout))

    def profileConnecting(self, client):
        client._xep_0198_session = ProfileSessionData(callback=self.checkAcks,
                                                      client=client)

    def getHandler(self, client):
        return XEP_0198_handler(self)

    def addHooks(self, client, receive_hooks, send_hooks):
        """Add hooks to handle in/out stanzas counters"""
        receive_hooks.append(partial(self.onReceive, client=client))
        send_hooks.append(partial(self.onSend, client=client))
        return True

    def _XMLInitTrigger(self, client):
        """Enable or resume a stream mangement"""
        if not (NS_SM, u'sm') in client.xmlstream.features:
            log.warning(_(
                u"Your server doesn't support stream management ({namespace}), this is "
                u"used to improve connection problems detection (like network outages). "
                u"Please ask your server administrator to enable this feature.".format(
                namespace=NS_SM)))
            return True
        session = client._xep_0198_session

        # a disconnect timer from a previous disconnection may still be active
        try:
            disconnect_timer = session.disconnect_timer
        except AttributeError:
            pass
        else:
            if disconnect_timer.active():
                disconnect_timer.cancel()
            del session.disconnect_timer

        if session.resume_enabled:
            # we are resuming a session
            resume_elt = domish.Element((NS_SM, 'resume'))
            resume_elt['h'] = unicode(session.in_counter)
            resume_elt['previd'] = session.session_id
            client.send(resume_elt)
            session.resuming = True
            # session.enabled will be set on <resumed/> reception
            return False
        else:
            # we start a new session
            assert session.out_counter == 0
            enable_elt = domish.Element((NS_SM, 'enable'))
            enable_elt[u'resume'] = u'true'
            client.send(enable_elt)
            session.enabled = True
            return True

    def _disconnectingTrigger(self, client):
        session = client._xep_0198_session
        if session.enabled:
            self.sendAck(client)
        # This is a requested disconnection, so we can reset the session
        # to disable resuming and close normally the stream
        session.reset()
        return True

    def _disconnectedTrigger(self, client, reason):
        if client.is_component:
            return True
        session = client._xep_0198_session
        session.enabled = False
        if session.resume_enabled:
            session.disconnected_time = time.time()
            session.disconnect_timer = reactor.callLater(session.session_max,
                                                         client.disconnectProfile,
                                                         reason)
            # disconnectProfile must not be called at this point
            # because session can be resumed
            return False
        else:
            return True

    def checkAcks(self, client):
        """Request ack if needed"""
        session = client._xep_0198_session
        # log.debug("checkAcks (in_counter={}, out_counter={}, buf len={}, buf idx={})"
        #     .format(session.in_counter, session.out_counter, len(session.buffer),
        #             session.buffer_idx))
        if session.ack_requested or not session.buffer:
            return
        if (session.out_counter - session.buffer_idx >= MAX_STANZA_ACK_R
            or time.time() - session.last_ack_r >= MAX_DELAY_ACK_R):
            self.requestAck(client)
            session.ack_requested = True
            session.last_ack_r = time.time()

    def updateBuffer(self, session, server_acked):
        """Update buffer and buffer_index"""
        if server_acked > session.buffer_idx:
            diff = server_acked - session.buffer_idx
            for i in xrange(diff):
                session.buffer.pop()
            session.buffer_idx += diff

    def sendAck(self, client):
        """Send an answer element with current IN counter"""
        a_elt = domish.Element((NS_SM, 'a'))
        a_elt['h'] = unicode(client._xep_0198_session.in_counter)
        client.send(a_elt)

    def requestAck(self, client):
        """Send a request element"""
        session = client._xep_0198_session
        r_elt = domish.Element((NS_SM, 'r'))
        client.send(r_elt)
        if session.req_timer is not None:
            raise exceptions.InternalError("req_timer should not be set")
        if self._ack_timeout:
            session.req_timer = reactor.callLater(self._ack_timeout, self.onAckTimeOut,
                                                  client)

    def _connectionFailed(self, failure_, connector):
        normal_host, normal_port = connector.normal_location
        del connector.normal_location
        log.warning(_(
            u"Connection failed using location given by server (host: {host}, port: "
            u"{port}), switching to normal host and port (host: {normal_host}, port: "
            u"{normal_port})".format(host=connector.host, port=connector.port,
                                     normal_host=normal_host, normal_port=normal_port)))
        connector.host, connector.port = normal_host, normal_port
        connector.connectionFailed = connector.connectionFailed_ori
        del connector.connectionFailed_ori
        return connector.connectionFailed(failure_)

    def onEnabled(self, enabled_elt, client):
        session = client._xep_0198_session
        session.in_counter = 0

        # we check that resuming is possible and that we have a session id
        resume = C.bool(enabled_elt.getAttribute(u'resume'))
        session_id = enabled_elt.getAttribute(u'id')
        if not session_id:
            log.warning(_(u'Incorrect <enabled/> element received, no "id" attribute'))
        if not resume or not session_id:
            log.warning(_(
                u"You're server doesn't support session resuming with stream management, "
                u"please contact your server administrator to enable it"))
            return

        session.session_id = session_id

        # XXX: we disable resource binding, which must not be done
        #      when we resume the session.
        client.factory.authenticator.res_binding = False

        # location, in case server want resuming session to be elsewhere
        try:
            location = enabled_elt[u'location']
        except KeyError:
            pass
        else:
            # TODO: handle IPv6 here (in brackets, cf. XEP)
            try:
                domain, port = location.split(':', 1)
                port = int(port)
            except ValueError:
                log.warning(_(u"Invalid location received: {location}")
                    .format(location=location))
            else:
                session.location = (domain, port)
                # we monkey patch connector to use the new location
                connector = client.xmlstream.transport.connector
                connector.normal_location = connector.host, connector.port
                connector.host = domain
                connector.port = port
                connector.connectionFailed_ori = connector.connectionFailed
                connector.connectionFailed = partial(self._connectionFailed,
                                                     connector=connector)

        # resuming time
        try:
            max_s = int(enabled_elt[u'max'])
        except (ValueError, KeyError) as e:
            if isinstance(e, ValueError):
                log.warning(_(u'Invalid "max" attribute'))
            max_s = RESUME_MAX
            log.info(_(u"Using default session max value ({max_s} s).".format(
                max_s=max_s)))
            log.info(_(u"Stream Management enabled"))
        else:
            log.info(_(
                u"Stream Management enabled, with a resumption time of {res_m} min"
                .format(res_m = max_s/60)))
        session.session_max = max_s

    def onResumed(self, enabled_elt, client):
        session = client._xep_0198_session
        assert not session.enabled
        del session.resuming
        server_acked = int(enabled_elt['h'])
        self.updateBuffer(session, server_acked)
        resend_count = len(session.buffer)
        # we resend all stanza which have not been received properly
        while True:
            try:
                stanza = session.buffer.pop()
            except IndexError:
                break
            else:
                client.send(stanza)
        # now we can continue the session
        session.enabled = True
        d_time = time.time() - session.disconnected_time
        log.info(_(u"Stream session resumed (disconnected for {d_time} s, {count} "
                   u"stanza(s) resent)").format(d_time=int(d_time), count=resend_count))

    def onFailed(self, failed_elt, client):
        session = client._xep_0198_session
        condition_elt = failed_elt.firstChildElement()
        session.reset()

        try:
            del session.resuming
        except AttributeError:
            # stream management can't be started at all
            msg = _(u"Can't use stream management")
            if condition_elt is None:
                log.error(msg + u'.')
            else:
                log.error(_(u"{msg}: {reason}").format(
                msg=msg, reason=condition_elt.name))
        else:
            # only stream resumption failed, we can try full session init
            # XXX: we try to start full session init from this point, with many
            #      variables/attributes already initialised with a potentially different
            #      jid. This is experimental and may not be safe. It may be more
            #      secured to abord the connection and restart everything with a fresh
            #      client.
            msg = _(u"stream resumption not possible, restarting full session")

            if condition_elt is None:
                log.warning(u'{msg}.'.format(msg=msg))
            else:
                log.warning(u"{msg}: {reason}".format(
                    msg=msg, reason=condition_elt.name))
            # stream resumption failed, but we still can do normal stream management
            # we restore attributes as if the session was new, and init stream
            # we keep everything initialized, and only do binding, roster request
            # and initial presence sending.
            if client.conn_deferred.called:
                client.conn_deferred = defer.Deferred()
            else:
                log.error(u"conn_deferred should be called at this point")
            # we need to recreate roster
            client.handlers.remove(client.roster)
            client.roster = client.roster.__class__(self.host)
            client.roster.setHandlerParent(client)
            # bind init is not done when resuming is possible, so we have to do it now
            bind_init = jabber_client.BindInitializer(client.xmlstream)
            bind_init.required = True
            d = bind_init.start()
            # we set the jid, which may have changed
            d.addCallback(lambda __: setattr(client.factory.authenticator, "jid", client.jid))
            # we call the trigger who will send the <enable/> element
            d.addCallback(lambda __: self._XMLInitTrigger(client))
            # then we have to re-request the roster, as changes may have occured
            d.addCallback(lambda __: client.roster.requestRoster())
            # we add got_roster to be sure to have roster before sending initial presence
            d.addCallback(lambda __: client.roster.got_roster)
            # initial presence must be sent manually
            d.addCallback(lambda __: client.presence.available())

    def onReceive(self, element, client):
        if not client.is_component:
            session = client._xep_0198_session
            if session.enabled and element.name.lower() in C.STANZA_NAMES:
                session.in_counter += 1 % MAX_COUNTER

    def onSend(self, obj, client):
        if not client.is_component:
            session = client._xep_0198_session
            if (session.enabled
                and domish.IElement.providedBy(obj)
                and obj.name.lower() in C.STANZA_NAMES):
                session.out_counter += 1 % MAX_COUNTER
                session.buffer.appendleft(obj)
                self.checkAcks(client)

    def onAckRequest(self, r_elt, client):
        self.sendAck(client)

    def onAckAnswer(self, a_elt, client):
        session = client._xep_0198_session
        session.ack_requested = False
        if self._ack_timeout:
            if session.req_timer is None:
                log.error("reg_timer should be set")
            else:
                session.req_timer.cancel()
                session.req_timer = None
        try:
            server_acked = int(a_elt['h'])
        except ValueError:
            log.warning(_(u"Server returned invalid ack element, disabling stream "
                          u"management: {xml}").format(xml=a_elt))
            session.enabled = False
            return

        if server_acked > session.out_counter:
            log.error(_(u"Server acked more stanzas than we have sent, disabling stream "
                        u"management."))
            session.reset()
            return

        self.updateBuffer(session, server_acked)
        self.checkAcks(client)

    def onAckTimeOut(self, client):
        """Called when a requested ACK has not been received in time"""
        log.info(_(u"Ack was not received in time, aborting connection"))
        client.xmlstream.transport.abortConnection()
        client._xep_0198_session.req_timer = None


class XEP_0198_handler(xmlstream.XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            SM_ENABLED, self.plugin_parent.onEnabled, client=self.parent
        )
        self.xmlstream.addObserver(
            SM_RESUMED, self.plugin_parent.onResumed, client=self.parent
        )
        self.xmlstream.addObserver(
            SM_FAILED, self.plugin_parent.onFailed, client=self.parent
        )
        self.xmlstream.addObserver(
            SM_R_REQUEST, self.plugin_parent.onAckRequest, client=self.parent
        )
        self.xmlstream.addObserver(
            SM_A_REQUEST, self.plugin_parent.onAckAnswer, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_SM)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

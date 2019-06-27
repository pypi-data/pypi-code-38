#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Chat State Notifications Protocol (xep-0085)
# Copyright (C) 2009-2016 Adrien Cossa (souliane@mailoo.org)

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
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.protocols.jabber.jid import JID

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler
from twisted.words.xish import domish
from twisted.internet import reactor
from twisted.internet import error as internet_error

NS_XMPP_CLIENT = "jabber:client"
NS_CHAT_STATES = "http://jabber.org/protocol/chatstates"
CHAT_STATES = ["active", "inactive", "gone", "composing", "paused"]
MESSAGE_TYPES = ["chat", "groupchat"]
PARAM_KEY = "Notifications"
PARAM_NAME = "Enable chat state notifications"
ENTITY_KEY = PARAM_KEY + "_" + PARAM_NAME
DELETE_VALUE = "DELETE"

PLUGIN_INFO = {
    C.PI_NAME: "Chat State Notifications Protocol Plugin",
    C.PI_IMPORT_NAME: "XEP-0085",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0085"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0085",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Chat State Notifications Protocol"""),
}


# Describe the internal transitions that are triggered
# by a timer. Beside that, external transitions can be
# runned to target the states "active" or "composing".
# Delay is specified here in seconds.
TRANSITIONS = {
    "active": {"next_state": "inactive", "delay": 120},
    "inactive": {"next_state": "gone", "delay": 480},
    "gone": {"next_state": "", "delay": 0},
    "composing": {"next_state": "paused", "delay": 30},
    "paused": {"next_state": "inactive", "delay": 450},
}


class UnknownChatStateException(Exception):
    """
    This error is raised when an unknown chat state is used.
    """

    pass


class XEP_0085(object):
    """
    Implementation for XEP 0085
    """

    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param name="%(param_name)s" label="%(param_label)s" value="true" type="bool" security="0"/>
     </category>
    </individual>
    </params>
    """ % {
        "category_name": PARAM_KEY,
        "category_label": _(PARAM_KEY),
        "param_name": PARAM_NAME,
        "param_label": _("Enable chat state notifications"),
    }

    def __init__(self, host):
        log.info(_("Chat State Notifications plugin initialization"))
        self.host = host
        self.map = {}  # FIXME: would be better to use client instead of mapping profile to data

        # parameter value is retrieved before each use
        host.memory.updateParams(self.params)

        # triggers from core
        host.trigger.add("MessageReceived", self.messageReceivedTrigger)
        host.trigger.add("sendMessage", self.sendMessageTrigger)
        host.trigger.add("paramUpdateTrigger", self.paramUpdateTrigger)

        # args: to_s (jid as string), profile
        host.bridge.addMethod(
            "chatStateComposing",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self.chatStateComposing,
        )

        # args: from (jid as string), state in CHAT_STATES, profile
        host.bridge.addSignal("chatStateReceived", ".plugin", signature="sss")

    def getHandler(self, client):
        return XEP_0085_handler(self, client.profile)

    def profileDisconnected(self, client):
        """Eventually send a 'gone' state to all one2one contacts."""
        profile = client.profile
        if profile not in self.map:
            return
        for to_jid in self.map[profile]:
            # FIXME: the "unavailable" presence stanza is received by to_jid
            # before the chat state, so it will be ignored... find a way to
            # actually defer the disconnection
            self.map[profile][to_jid]._onEvent("gone")
        del self.map[profile]

    def updateCache(self, entity_jid, value, profile):
        """Update the entity data of the given profile for one or all contacts.
        Reset the chat state(s) display if the notification has been disabled.

        @param entity_jid: contact's JID, or C.ENTITY_ALL to update all contacts.
        @param value: True, False or DELETE_VALUE to delete the entity data
        @param profile: current profile
        """
        if value == DELETE_VALUE:
            self.host.memory.delEntityDatum(entity_jid, ENTITY_KEY, profile)
        else:
            self.host.memory.updateEntityData(
                entity_jid, ENTITY_KEY, value, profile_key=profile
            )
        if not value or value == DELETE_VALUE:
            # reinit chat state UI for this or these contact(s)
            self.host.bridge.chatStateReceived(entity_jid.full(), "", profile)

    def paramUpdateTrigger(self, name, value, category, type_, profile):
        """Reset all the existing chat state entity data associated with this profile after a parameter modification.

        @param name: parameter name
        @param value: "true" to activate the notifications, or any other value to delete it
        @param category: parameter category
        @param type_: parameter type
        """
        if (category, name) == (PARAM_KEY, PARAM_NAME):
            self.updateCache(
                C.ENTITY_ALL, True if C.bool(value) else DELETE_VALUE, profile=profile
            )
            return False
        return True

    def messageReceivedTrigger(self, client, message, post_treat):
        """
        Update the entity cache when we receive a message with body.
        Check for a chat state in the message and signal frontends.
        """
        profile = client.profile
        if not self.host.memory.getParamA(PARAM_NAME, PARAM_KEY, profile_key=profile):
            return True

        from_jid = JID(message.getAttribute("from"))
        if self._isMUC(from_jid, profile):
            from_jid = from_jid.userhostJID()
        else:  # update entity data for one2one chat
            # assert from_jid.resource # FIXME: assert doesn't work on normal message from server (e.g. server announce), because there is no resource
            try:
                domish.generateElementsNamed(message.elements(), name="body").next()
                try:
                    domish.generateElementsNamed(message.elements(), name="active").next()
                    # contact enabled Chat State Notifications
                    self.updateCache(from_jid, True, profile=profile)
                except StopIteration:
                    if message.getAttribute("type") == "chat":
                        # contact didn't enable Chat State Notifications
                        self.updateCache(from_jid, False, profile=profile)
                        return True
            except StopIteration:
                pass

        # send our next "composing" states to any MUC and to the contacts who enabled the feature
        self._chatStateInit(from_jid, message.getAttribute("type"), profile)

        state_list = [
            child.name
            for child in message.elements()
            if message.getAttribute("type") in MESSAGE_TYPES
            and child.name in CHAT_STATES
            and child.defaultUri == NS_CHAT_STATES
        ]
        for state in state_list:
            # there must be only one state according to the XEP
            if state != "gone" or message.getAttribute("type") != "groupchat":
                self.host.bridge.chatStateReceived(
                    message.getAttribute("from"), state, profile
                )
            break
        return True

    def sendMessageTrigger(
        self, client, mess_data, pre_xml_treatments, post_xml_treatments
    ):
        """
        Eventually add the chat state to the message and initiate
        the state machine when sending an "active" state.
        """
        profile = client.profile

        def treatment(mess_data):
            message = mess_data["xml"]
            to_jid = JID(message.getAttribute("to"))
            if not self._checkActivation(to_jid, forceEntityData=True, profile=profile):
                return mess_data
            try:
                # message with a body always mean active state
                domish.generateElementsNamed(message.elements(), name="body").next()
                message.addElement("active", NS_CHAT_STATES)
                # launch the chat state machine (init the timer)
                if self._isMUC(to_jid, profile):
                    to_jid = to_jid.userhostJID()
                self._chatStateActive(to_jid, mess_data["type"], profile)
            except StopIteration:
                if "chat_state" in mess_data["extra"]:
                    state = mess_data["extra"].pop("chat_state")
                    assert state in CHAT_STATES
                    message.addElement(state, NS_CHAT_STATES)
            return mess_data

        post_xml_treatments.addCallback(treatment)
        return True

    def _isMUC(self, to_jid, profile):
        """Tell if that JID is a MUC or not

        @param to_jid (JID): full or bare JID to check
        @param profile (str): %(doc_profile)s
        @return: bool
        """
        try:
            type_ = self.host.memory.getEntityDatum(to_jid.userhostJID(), "type", profile)
            if type_ == "chatroom":  # FIXME: should not use disco instead ?
                return True
        except (exceptions.UnknownEntityError, KeyError):
            pass
        return False

    def _checkActivation(self, to_jid, forceEntityData, profile):
        """
        @param to_jid: the contact's full JID (or bare if you know it's a MUC)
        @param forceEntityData: if set to True, a non-existing
        entity data will be considered to be True (and initialized)
        @param: current profile
        @return: True if the notifications should be sent to this JID.
        """
        # check if the parameter is active
        if not self.host.memory.getParamA(PARAM_NAME, PARAM_KEY, profile_key=profile):
            return False
        # check if notifications should be sent to this contact
        if self._isMUC(to_jid, profile):
            return True
        # FIXME: this assertion crash when we want to send a message to an online bare jid
        # assert to_jid.resource or not self.host.memory.isEntityAvailable(to_jid, profile) # must either have a resource, or talk to an offline contact
        try:
            return self.host.memory.getEntityDatum(to_jid, ENTITY_KEY, profile)
        except (exceptions.UnknownEntityError, KeyError):
            if forceEntityData:
                # enable it for the first time
                self.updateCache(to_jid, True, profile=profile)
                return True
        # wait for the first message before sending states
        return False

    def _chatStateInit(self, to_jid, mess_type, profile):
        """
        Data initialization for the chat state machine.

        @param to_jid (JID): full JID for one2one, bare JID for MUC
        @param mess_type (str): "one2one" or "groupchat"
        @param profile (str): %(doc_profile)s
        """
        if mess_type is None:
            return
        profile_map = self.map.setdefault(profile, {})
        if to_jid not in profile_map:
            machine = ChatStateMachine(self.host, to_jid, mess_type, profile)
            self.map[profile][to_jid] = machine

    def _chatStateActive(self, to_jid, mess_type, profile_key):
        """
        Launch the chat state machine on "active" state.

        @param to_jid (JID): full JID for one2one, bare JID for MUC
        @param mess_type (str): "one2one" or "groupchat"
        @param profile (str): %(doc_profile)s
        """
        profile = self.host.memory.getProfileName(profile_key)
        if profile is None:
            raise exceptions.ProfileUnknownError
        self._chatStateInit(to_jid, mess_type, profile)
        self.map[profile][to_jid]._onEvent("active")

    def chatStateComposing(self, to_jid_s, profile_key):
        """Move to the "composing" state when required.

        Since this method is called from the front-end, it needs to check the
        values of the parameter "Send chat state notifications" and the entity
        data associated to the target JID.

        @param to_jid_s (str): contact full JID as a string
        @param profile_key (str): %(doc_profile_key)s
        """
        # TODO: try to optimize this method which is called often
        client = self.host.getClient(profile_key)
        to_jid = JID(to_jid_s)
        if self._isMUC(to_jid, client.profile):
            to_jid = to_jid.userhostJID()
        elif not to_jid.resource:
            to_jid.resource = self.host.memory.getMainResource(client, to_jid)
        if not self._checkActivation(
            to_jid, forceEntityData=False, profile=client.profile
        ):
            return
        try:
            self.map[client.profile][to_jid]._onEvent("composing")
        except (KeyError, AttributeError):
            # no message has been sent/received since the notifications
            # have been enabled, it's better to wait for a first one
            pass


class ChatStateMachine(object):
    """
    This class represents a chat state, between one profile and
    one target contact. A timer is used to move from one state
    to the other. The initialization is done through the "active"
    state which is internally set when a message is sent. The state
    "composing" can be set externally (through the bridge by a
    frontend). Other states are automatically set with the timer.
    """

    def __init__(self, host, to_jid, mess_type, profile):
        """
        Initialization need to store the target, message type
        and a profile for sending later messages.
        """
        self.host = host
        self.to_jid = to_jid
        self.mess_type = mess_type
        self.profile = profile
        self.state = None
        self.timer = None

    def _onEvent(self, state):
        """
        Move to the specified state, eventually send the
        notification to the contact (the "active" state is
        automatically sent with each message) and set the timer.
        """
        assert state in TRANSITIONS
        transition = TRANSITIONS[state]
        assert "next_state" in transition and "delay" in transition

        if state != self.state and state != "active":
            if state != "gone" or self.mess_type != "groupchat":
                # send a new message without body
                log.debug(
                    u"sending state '{state}' to {jid}".format(
                        state=state, jid=self.to_jid.full()
                    )
                )
                client = self.host.getClient(self.profile)
                mess_data = {
                    "from": client.jid,
                    "to": self.to_jid,
                    "uid": "",
                    "message": {},
                    "type": self.mess_type,
                    "subject": {},
                    "extra": {},
                }
                client.generateMessageXML(mess_data)
                mess_data["xml"].addElement(state, NS_CHAT_STATES)
                client.send(mess_data["xml"])

        self.state = state
        try:
            self.timer.cancel()
        except (internet_error.AlreadyCalled, AttributeError):
            pass

        if transition["next_state"] and transition["delay"] > 0:
            self.timer = reactor.callLater(
                transition["delay"], self._onEvent, transition["next_state"]
            )


class XEP_0085_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_CHAT_STATES)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

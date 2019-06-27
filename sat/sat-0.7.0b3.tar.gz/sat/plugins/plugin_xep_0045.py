#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0045
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
log = getLogger(__name__)
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.python import failure

from sat.core import exceptions
from sat.memory import memory

import time
import uuid

from wokkel import muc, disco, iwokkel
from sat.tools import xml_tools

from zope.interface import implements

# XXX: mam and rsm come from sat_tmp.wokkel
from wokkel import rsm
from wokkel import mam


PLUGIN_INFO = {
    C.PI_NAME: "XEP-0045 Plugin",
    C.PI_IMPORT_NAME: "XEP-0045",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0045"],
    C.PI_DEPENDENCIES: ["XEP-0359"],
    C.PI_RECOMMENDATIONS: [C.TEXT_CMDS, u"XEP-0313"],
    C.PI_MAIN: "XEP_0045",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Multi-User Chat""")
}

NS_MUC = 'http://jabber.org/protocol/muc'
AFFILIATIONS = ('owner', 'admin', 'member', 'none', 'outcast')
ROOM_USER_JOINED = 'ROOM_USER_JOINED'
ROOM_USER_LEFT = 'ROOM_USER_LEFT'
OCCUPANT_KEYS = ('nick', 'entity', 'affiliation', 'role')
ENTITY_TYPE_MUC = "MUC"
ROOM_STATE_OCCUPANTS = "occupants"
ROOM_STATE_SELF_PRESENCE = "self-presence"
ROOM_STATE_LIVE = "live"
ROOM_STATES = (ROOM_STATE_OCCUPANTS, ROOM_STATE_SELF_PRESENCE, ROOM_STATE_LIVE)
HISTORY_LEGACY = u"legacy"
HISTORY_MAM = u"mam"


CONFIG_SECTION = u'plugin muc'

default_conf = {"default_muc": u'sat@chat.jabberfr.org'}


class AlreadyJoined(exceptions.ConflictError):

    def __init__(self, room):
        super(AlreadyJoined, self).__init__()
        self.room = room


class XEP_0045(object):
    # TODO: handle invitations
    # FIXME: this plugin need a good cleaning, join method is messy

    def __init__(self, host):
        log.info(_("Plugin XEP_0045 initialization"))
        self.host = host
        self._sessions = memory.Sessions()
        host.bridge.addMethod("mucJoin", ".plugin", in_sign='ssa{ss}s', out_sign='(bsa{sa{ss}}sss)', method=self._join, async=True)  # return same arguments as mucRoomJoined + a boolean set to True is the room was already joined (first argument)
        host.bridge.addMethod("mucNick", ".plugin", in_sign='sss', out_sign='', method=self._nick)
        host.bridge.addMethod("mucNickGet", ".plugin", in_sign='ss', out_sign='s', method=self._getRoomNick)
        host.bridge.addMethod("mucLeave", ".plugin", in_sign='ss', out_sign='', method=self._leave, async=True)
        host.bridge.addMethod("mucOccupantsGet", ".plugin", in_sign='ss', out_sign='a{sa{ss}}', method=self._getRoomOccupants)
        host.bridge.addMethod("mucSubject", ".plugin", in_sign='sss', out_sign='', method=self._subject)
        host.bridge.addMethod("mucGetRoomsJoined", ".plugin", in_sign='s', out_sign='a(sa{sa{ss}}ss)', method=self._getRoomsJoined)
        host.bridge.addMethod("mucGetUniqueRoomName", ".plugin", in_sign='ss', out_sign='s', method=self._getUniqueName)
        host.bridge.addMethod("mucConfigureRoom", ".plugin", in_sign='ss', out_sign='s', method=self._configureRoom, async=True)
        host.bridge.addMethod("mucGetDefaultService", ".plugin", in_sign='', out_sign='s', method=self.getDefaultMUC)
        host.bridge.addMethod("mucGetService", ".plugin", in_sign='ss', out_sign='s', method=self._getMUCService, async=True)
        host.bridge.addSignal("mucRoomJoined", ".plugin", signature='sa{sa{ss}}sss')  # args: room_jid, occupants, user_nick, subject, profile
        host.bridge.addSignal("mucRoomLeft", ".plugin", signature='ss')  # args: room_jid, profile
        host.bridge.addSignal("mucRoomUserChangedNick", ".plugin", signature='ssss')  # args: room_jid, old_nick, new_nick, profile
        host.bridge.addSignal("mucRoomNewSubject", ".plugin", signature='sss')  # args: room_jid, subject, profile
        self.__submit_conf_id = host.registerCallback(self._submitConfiguration, with_data=True)
        self._room_join_id = host.registerCallback(self._UIRoomJoinCb, with_data=True)
        host.importMenu((D_("MUC"), D_("configure")), self._configureRoomMenu, security_limit=0, help_string=D_("Configure Multi-User Chat room"), type_=C.MENU_ROOM)
        try:
            self.text_cmds = self.host.plugins[C.TEXT_CMDS]
        except KeyError:
            log.info(_(u"Text commands not available"))
        else:
            self.text_cmds.registerTextCommands(self)
            self.text_cmds.addWhoIsCb(self._whois, 100)

        self._mam = self.host.plugins.get(u"XEP-0313")
        self._si = self.host.plugins[u"XEP-0359"]

        host.trigger.add("presence_available", self.presenceTrigger)
        host.trigger.add("presence_received", self.presenceReceivedTrigger)
        host.trigger.add("MessageReceived", self.messageReceivedTrigger, priority=1000000)
        host.trigger.add("message_parse", self._message_parseTrigger)

    def profileConnected(self, client):
        def assign_service(service):
            client.muc_service = service
        return self.getMUCService(client).addCallback(assign_service)

    def _message_parseTrigger(self, client, message_elt, data):
        """Add stanza-id from the room if present"""
        if message_elt.getAttribute(u"type") != C.MESS_TYPE_GROUPCHAT:
            return True

        # stanza_id will not be filled by parseMessage because the emitter
        # is the room and not our server, so we have to parse it here
        room_jid = data[u"from"].userhostJID()
        stanza_id = self._si.getStanzaId(message_elt, room_jid)
        if stanza_id:
            data[u"extra"][u"stanza_id"] = stanza_id

    def messageReceivedTrigger(self, client, message_elt, post_treat):
        if message_elt.getAttribute("type") == C.MESS_TYPE_GROUPCHAT:
            if message_elt.subject or message_elt.delay:
                return False
            from_jid = jid.JID(message_elt['from'])
            room_jid = from_jid.userhostJID()
            if room_jid in client._muc_client.joined_rooms:
                room = client._muc_client.joined_rooms[room_jid]
                if room.state != ROOM_STATE_LIVE:
                    if getattr(room, "_history_type", HISTORY_LEGACY) == HISTORY_LEGACY:
                        # With MAM history, order is different, and we can get live
                        # messages before history is complete, so this is not a warning
                        # but an expected case.
                        # On the other hand, with legacy history, it's not normal.
                        log.warning(_(
                            u"Received non delayed message in a room before its "
                            u"initialisation: state={state}, msg={msg}").format(
                        state=room.state,
                        msg=message_elt.toXml()))
                    room._cache.append(message_elt)
                    return False
            else:
                log.warning(u"Received groupchat message for a room which has not been "
                            u"joined, ignoring it: {}".format(message_elt.toXml()))
                return False
        return True

    def getRoom(self, client, room_jid):
        """Retrieve Room instance from its jid

        @param room_jid(jid.JID): jid of the room
        @raise exceptions.NotFound: the room has not been joined
        """
        try:
            return client._muc_client.joined_rooms[room_jid]
        except KeyError:
            raise exceptions.NotFound(_(u"This room has not been joined"))

    def checkRoomJoined(self, client, room_jid):
        """Check that given room has been joined in current session

        @param room_jid (JID): room JID
        """
        if room_jid not in client._muc_client.joined_rooms:
            raise exceptions.NotFound(_(u"This room has not been joined"))

    def isJoinedRoom(self, client, room_jid):
        """Tell if a jid is a known and joined room

        @room_jid(jid.JID): jid of the room
        """
        try:
            self.checkRoomJoined(client, room_jid)
        except exceptions.NotFound:
            return False
        else:
            return True

    def _getRoomJoinedArgs(self, room, profile):
        return [
            room.roomJID.userhost(),
            XEP_0045._getOccupants(room),
            room.nick,
            room.subject,
            profile
            ]

    def _UIRoomJoinCb(self, data, profile):
        room_jid = jid.JID(data['index'])
        client = self.host.getClient(profile)
        self.join(client, room_jid)
        return {}

    def _passwordUICb(self, data, client, room_jid, nick):
        """Called when the user has given room password (or cancelled)"""
        if C.bool(data.get(C.XMLUI_DATA_CANCELLED, "false")):
            log.info(u"room join for {} is cancelled".format(room_jid.userhost()))
            raise failure.Failure(exceptions.CancelError(D_(u"Room joining cancelled by user")))
        password = data[xml_tools.formEscape('password')]
        return client._muc_client.join(room_jid, nick, password).addCallbacks(self._joinCb, self._joinEb, (client, room_jid, nick), errbackArgs=(client, room_jid, nick, password))

    def _showListUI(self, items, client, service):
        xmlui = xml_tools.XMLUI(title=D_('Rooms in {}'.format(service.full())))
        adv_list = xmlui.changeContainer('advanced_list', columns=1, selectable='single', callback_id=self._room_join_id)
        items = sorted(items, key=lambda i: i.name.lower())
        for item in items:
            adv_list.setRowIndex(item.entity.full())
            xmlui.addText(item.name)
        adv_list.end()
        self.host.actionNew({'xmlui': xmlui.toXml()}, profile=client.profile)

    def _joinCb(self, room, client, room_jid, nick):
        """Called when the user is in the requested room"""
        if room.locked:
            # FIXME: the current behaviour is to create an instant room
            # and send the signal only when the room is unlocked
            # a proper configuration management should be done
            log.debug(_(u"room locked !"))
            d = client._muc_client.configure(room.roomJID, {})
            d.addErrback(lambda __: log.error(_(u'Error while configuring the room')))
        return room.fully_joined

    def _joinEb(self, failure, client, room_jid, nick, password):
        """Called when something is going wrong when joining the room"""
        try:
            condition = failure.value.condition
        except AttributeError:
            msg_suffix = ''
        else:
            if condition == 'conflict':
                # we have a nickname conflict, we try again with "_" suffixed to current nickname
                nick += '_'
                return client._muc_client.join(room_jid, nick, password).addCallbacks(self._joinCb, self._joinEb, (client, room_jid, nick), errbackArgs=(client, room_jid, nick, password))
            elif condition == 'not-allowed':
                # room is restricted, we need a password
                password_ui = xml_tools.XMLUI("form", title=D_(u'Room {} is restricted').format(room_jid.userhost()), submit_id='')
                password_ui.addText(D_("This room is restricted, please enter the password"))
                password_ui.addPassword('password')
                d = xml_tools.deferXMLUI(self.host, password_ui, profile=client.profile)
                d.addCallback(self._passwordUICb, client, room_jid, nick)
                return d

            msg_suffix = ' with condition "{}"'.format(failure.value.condition)

        mess = D_(u"Error while joining the room {room}{suffix}".format(
            room = room_jid.userhost(), suffix = msg_suffix))
        log.error(mess)
        xmlui = xml_tools.note(mess, D_(u"Group chat error"), level=C.XMLUI_DATA_LVL_ERROR)
        self.host.actionNew({'xmlui': xmlui.toXml()}, profile=client.profile)

    @staticmethod
    def _getOccupants(room):
        """Get occupants of a room in a form suitable for bridge"""
        return {u.nick: {k:unicode(getattr(u,k) or '') for k in OCCUPANT_KEYS} for u in room.roster.values()}

    def _getRoomOccupants(self, room_jid_s, profile_key):
        client = self.host.getClient(profile_key)
        room_jid = jid.JID(room_jid_s)
        return self.getRoomOccupants(client, room_jid)

    def getRoomOccupants(self, client, room_jid):
        room = self.getRoom(client, room_jid)
        return self._getOccupants(room)

    def _getRoomsJoined(self, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        return self.getRoomsJoined(client)

    def getRoomsJoined(self, client):
        """Return rooms where user is"""
        result = []
        for room in client._muc_client.joined_rooms.values():
            if room.state == ROOM_STATE_LIVE:
                result.append((room.roomJID.userhost(), self._getOccupants(room), room.nick, room.subject))
        return result

    def _getRoomNick(self, room_jid_s, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        return self.getRoomNick(client, jid.JID(room_jid_s))

    def getRoomNick(self, client, room_jid):
        """return nick used in room by user

        @param room_jid (jid.JID): JID of the room
        @profile_key: profile
        @return: nick or empty string in case of error
        @raise exceptions.Notfound: use has not joined the room
        """
        self.checkRoomJoined(client, room_jid)
        return client._muc_client.joined_rooms[room_jid].nick

    def _configureRoom(self, room_jid_s, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        d = self.configureRoom(client, jid.JID(room_jid_s))
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def _configureRoomMenu(self, menu_data, profile):
        """Return room configuration form

        @param menu_data: %(menu_data)s
        @param profile: %(doc_profile)s
        """
        client = self.host.getClient(profile)
        try:
            room_jid = jid.JID(menu_data['room_jid'])
        except KeyError:
            log.error(_("room_jid key is not present !"))
            return defer.fail(exceptions.DataError)

        def xmluiReceived(xmlui):
            if not xmlui:
                msg = D_(u"No configuration available for this room")
                return {"xmlui": xml_tools.note(msg).toXml()}
            return {"xmlui": xmlui.toXml()}
        return self.configureRoom(client, room_jid).addCallback(xmluiReceived)

    def configureRoom(self, client, room_jid):
        """return the room configuration form

        @param room: jid of the room to configure
        @return: configuration form as XMLUI
        """
        self.checkRoomJoined(client, room_jid)

        def config2XMLUI(result):
            if not result:
                return ""
            session_id, session_data = self._sessions.newSession(profile=client.profile)
            session_data["room_jid"] = room_jid
            xmlui = xml_tools.dataForm2XMLUI(result, submit_id=self.__submit_conf_id)
            xmlui.session_id = session_id
            return xmlui

        d = client._muc_client.getConfiguration(room_jid)
        d.addCallback(config2XMLUI)
        return d

    def _submitConfiguration(self, raw_data, profile):
        cancelled = C.bool(raw_data.get("cancelled", C.BOOL_FALSE))
        if cancelled:
            return defer.succeed({})
        client = self.host.getClient(profile)
        try:
            session_data = self._sessions.profileGet(raw_data["session_id"], profile)
        except KeyError:
            log.warning(D_("Session ID doesn't exist, session has probably expired."))
            _dialog = xml_tools.XMLUI('popup', title=D_('Room configuration failed'))
            _dialog.addText(D_("Session ID doesn't exist, session has probably expired."))
            return defer.succeed({'xmlui': _dialog.toXml()})

        data = xml_tools.XMLUIResult2DataFormResult(raw_data)
        d = client._muc_client.configure(session_data['room_jid'], data)
        _dialog = xml_tools.XMLUI('popup', title=D_('Room configuration succeed'))
        _dialog.addText(D_("The new settings have been saved."))
        d.addCallback(lambda ignore: {'xmlui': _dialog.toXml()})
        del self._sessions[raw_data["session_id"]]
        return d

    def isNickInRoom(self, client, room_jid, nick):
        """Tell if a nick is currently present in a room"""
        self.checkRoomJoined(client, room_jid)
        return client._muc_client.joined_rooms[room_jid].inRoster(muc.User(nick))

    def _getMUCService(self, jid_=None, profile=C.PROF_KEY_NONE):
        client = self.host.getClient(profile)
        d = self.getMUCService(client, jid_ or None)
        d.addCallback(lambda service_jid: service_jid.full() if service_jid is not None else u'')
        return d

    @defer.inlineCallbacks
    def getMUCService(self, client, jid_=None):
        """Return first found MUC service of an entity

        @param jid_: entity which may have a MUC service, or None for our own server
        @return (jid.JID, None): found service jid or None
        """
        if jid_ is None:
            try:
                muc_service = client.muc_service
            except AttributeError:
                pass
            else:
                # we have a cached value, we return it
                defer.returnValue(muc_service)
        services = yield self.host.findServiceEntities(client, "conference", "text", jid_)
        for service in services:
            if ".irc." not in service.userhost():
                # FIXME:
                # This ugly hack is here to avoid an issue with openfire: the IRC gateway
                # use "conference/text" identity (instead of "conference/irc")
                muc_service = service
                break
        else:
            muc_service = None
        defer.returnValue(muc_service)

    def _getUniqueName(self, muc_service="", profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        return self.getUniqueName(client, muc_service or None).full()

    def getUniqueName(self, client, muc_service=None):
        """Return unique name for a room, avoiding collision

        @param muc_service (jid.JID) : leave empty string to use the default service
        @return: jid.JID (unique room bare JID)
        """
        # TODO: we should use #RFC-0045 10.1.4 when available here
        room_name = unicode(uuid.uuid4())
        if muc_service is None:
            try:
                muc_service = client.muc_service
            except AttributeError:
                raise exceptions.NotReady(u"Main server MUC service has not been checked yet")
            if muc_service is None:
                log.warning(_("No MUC service found on main server"))
                raise exceptions.FeatureNotFound

        muc_service = muc_service.userhost()
        return jid.JID(u"{}@{}".format(room_name, muc_service))

    def getDefaultMUC(self):
        """Return the default MUC.

        @return: unicode
        """
        return self.host.memory.getConfig(CONFIG_SECTION, 'default_muc', default_conf['default_muc'])

    def _join_eb(self, failure_, client):
        failure_.trap(AlreadyJoined)
        room = failure_.value.room
        return [True] + self._getRoomJoinedArgs(room, client.profile)

    def _join(self, room_jid_s, nick, options, profile_key=C.PROF_KEY_NONE):
        """join method used by bridge

        @return (tuple): already_joined boolean + room joined arguments (see [_getRoomJoinedArgs])
        """
        client = self.host.getClient(profile_key)
        if room_jid_s:
            muc_service = client.muc_service
            try:
                room_jid = jid.JID(room_jid_s)
            except (RuntimeError, jid.InvalidFormat, AttributeError):
                return defer.fail(jid.InvalidFormat(_(u"Invalid room identifier: {room_id}'. Please give a room short or full identifier like 'room' or 'room@{muc_service}'.").format(
                    room_id=room_jid_s,
                    muc_service=unicode(muc_service))))
            if not room_jid.user:
                room_jid.user, room_jid.host = room_jid.host, muc_service
        else:
            room_jid = self.getUniqueName(profile_key=client.profile)
        # TODO: error management + signal in bridge
        d = self.join(client, room_jid, nick, options or None)
        d.addCallback(lambda room: [False] + self._getRoomJoinedArgs(room, client.profile))
        d.addErrback(self._join_eb, client)
        return d

    def join(self, client, room_jid, nick=None, options=None):
        if not nick:
            nick = client.jid.user
        if options is None:
            options = {}
        if room_jid in client._muc_client.joined_rooms:
            room = client._muc_client.joined_rooms[room_jid]
            log.info(_(u'{profile} is already in room {room_jid}').format(profile=client.profile, room_jid = room_jid.userhost()))
            return defer.fail(AlreadyJoined(room))
        log.info(_(u"[{profile}] is joining room {room} with nick {nick}").format(profile=client.profile, room=room_jid.userhost(), nick=nick))

        password = options.get("password")

        return client._muc_client.join(room_jid, nick, password).addCallbacks(self._joinCb, self._joinEb, (client, room_jid, nick), errbackArgs=(client, room_jid, nick, password))

    def _nick(self, room_jid_s, nick, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        return self.nick(client, jid.JID(room_jid_s), nick)

    def nick(self, client, room_jid, nick):
        """Change nickname in a room"""
        self.checkRoomJoined(client, room_jid)
        return client._muc_client.nick(room_jid, nick)

    def _leave(self, room_jid, profile_key):
        client = self.host.getClient(profile_key)
        return self.leave(client, jid.JID(room_jid))

    def leave(self, client, room_jid):
        self.checkRoomJoined(client, room_jid)
        return client._muc_client.leave(room_jid)

    def _subject(self, room_jid_s, new_subject, profile_key):
        client = self.host.getClient(profile_key)
        return self.subject(client, jid.JID(room_jid_s), new_subject)

    def subject(self, client, room_jid, subject):
        self.checkRoomJoined(client, room_jid)
        return client._muc_client.subject(room_jid, subject)

    def getHandler(self, client):
        # create a MUC client and associate it with profile' session
        muc_client = client._muc_client = SatMUCClient(self)
        return muc_client

    def kick(self, client, nick, room_jid, options=None):
        """Kick a participant from the room

        @param nick (str): nick of the user to kick
        @param room_jid_s (JID): jid of the room
        @param options (dict): attribute with extra info (reason, password) as in #XEP-0045
        """
        if options is None:
            options = {}
        self.checkRoomJoined(client, room_jid)
        return client._muc_client.kick(room_jid, nick, reason=options.get('reason', None))

    def ban(self, client, entity_jid, room_jid, options=None):
        """Ban an entity from the room

        @param entity_jid (JID): bare jid of the entity to be banned
        @param room_jid (JID): jid of the room
        @param options: attribute with extra info (reason, password) as in #XEP-0045
        """
        self.checkRoomJoined(client, room_jid)
        if options is None:
            options = {}
        assert not entity_jid.resource
        assert not room_jid.resource
        return client._muc_client.ban(room_jid, entity_jid, reason=options.get('reason', None))

    def affiliate(self, client, entity_jid, room_jid, options):
        """Change the affiliation of an entity

        @param entity_jid (JID): bare jid of the entity
        @param room_jid_s (JID): jid of the room
        @param options: attribute with extra info (reason, nick) as in #XEP-0045
        """
        self.checkRoomJoined(client, room_jid)
        assert not entity_jid.resource
        assert not room_jid.resource
        assert 'affiliation' in options
        # TODO: handles reason and nick
        return client._muc_client.modifyAffiliationList(room_jid, [entity_jid], options['affiliation'])

    # Text commands #

    def cmd_nick(self, client, mess_data):
        """change nickname

        @command (group): new_nick
            - new_nick: new nick to use
        """
        nick = mess_data["unparsed"].strip()
        if nick:
            room = mess_data["to"]
            self.nick(client, room, nick)

        return False

    def cmd_join(self, client, mess_data):
        """join a new room

        @command (all): JID
            - JID: room to join (on the same service if full jid is not specified)
        """
        if mess_data["unparsed"].strip():
            room_jid = self.text_cmds.getRoomJID(mess_data["unparsed"].strip(), mess_data["to"].host)
            nick = (self.getRoomNick(client, room_jid) or
                    client.jid.user)
            self.join(client, room_jid, nick, {})

        return False

    def cmd_leave(self, client, mess_data):
        """quit a room

        @command (group): [ROOM_JID]
            - ROOM_JID: jid of the room to live (current room if not specified)
        """
        if mess_data["unparsed"].strip():
            room = self.text_cmds.getRoomJID(mess_data["unparsed"].strip(), mess_data["to"].host)
        else:
            room = mess_data["to"]

        self.leave(client, room)

        return False

    def cmd_part(self, client, mess_data):
        """just a synonym of /leave

        @command (group): [ROOM_JID]
            - ROOM_JID: jid of the room to live (current room if not specified)
        """
        return self.cmd_leave(client, mess_data)

    def cmd_kick(self, client, mess_data):
        """kick a room member

        @command (group): ROOM_NICK
            - ROOM_NICK: the nick of the person to kick
        """
        options = mess_data["unparsed"].strip().split()
        try:
            nick = options[0]
            assert self.isNickInRoom(client, mess_data["to"], nick)
        except (IndexError, AssertionError):
            feedback = _(u"You must provide a member's nick to kick.")
            self.text_cmds.feedBack(client, feedback, mess_data)
            return False

        d = self.kick(client, nick, mess_data["to"], {} if len(options) == 1 else {'reason': options[1]})

        def cb(__):
            feedback_msg = _(u'You have kicked {}').format(nick)
            if len(options) > 1:
                feedback_msg += _(u' for the following reason: {}').format(options[1])
            self.text_cmds.feedBack(client, feedback_msg, mess_data)
            return True
        d.addCallback(cb)
        return d

    def cmd_ban(self, client, mess_data):
        """ban an entity from the room

        @command (group): (JID) [reason]
            - JID: the JID of the entity to ban
            - reason: the reason why this entity is being banned
        """
        options = mess_data["unparsed"].strip().split()
        try:
            jid_s = options[0]
            entity_jid = jid.JID(jid_s).userhostJID()
            assert(entity_jid.user)
            assert(entity_jid.host)
        except (RuntimeError, jid.InvalidFormat, AttributeError, IndexError, AssertionError):
            feedback = _(u"You must provide a valid JID to ban, like in '/ban contact@example.net'")
            self.text_cmds.feedBack(client, feedback, mess_data)
            return False

        d = self.ban(client, entity_jid, mess_data["to"], {} if len(options) == 1 else {'reason': options[1]})

        def cb(__):
            feedback_msg = _(u'You have banned {}').format(entity_jid)
            if len(options) > 1:
                feedback_msg += _(u' for the following reason: {}').format(options[1])
            self.text_cmds.feedBack(client, feedback_msg, mess_data)
            return True
        d.addCallback(cb)
        return d

    def cmd_affiliate(self, client, mess_data):
        """affiliate an entity to the room

        @command (group): (JID) [owner|admin|member|none|outcast]
            - JID: the JID of the entity to affiliate
            - owner: grant owner privileges
            - admin: grant admin privileges
            - member: grant member privileges
            - none: reset entity privileges
            - outcast: ban entity
        """
        options = mess_data["unparsed"].strip().split()
        try:
            jid_s = options[0]
            entity_jid = jid.JID(jid_s).userhostJID()
            assert(entity_jid.user)
            assert(entity_jid.host)
        except (RuntimeError, jid.InvalidFormat, AttributeError, IndexError, AssertionError):
            feedback = _(u"You must provide a valid JID to affiliate, like in '/affiliate contact@example.net member'")
            self.text_cmds.feedBack(client, feedback, mess_data)
            return False

        affiliation = options[1] if len(options) > 1 else 'none'
        if affiliation not in AFFILIATIONS:
            feedback = _(u"You must provide a valid affiliation: %s") % ' '.join(AFFILIATIONS)
            self.text_cmds.feedBack(client, feedback, mess_data)
            return False

        d = self.affiliate(client, entity_jid, mess_data["to"], {'affiliation': affiliation})

        def cb(__):
            feedback_msg = _(u'New affiliation for %(entity)s: %(affiliation)s').format(entity=entity_jid, affiliation=affiliation)
            self.text_cmds.feedBack(client, feedback_msg, mess_data)
            return True
        d.addCallback(cb)
        return d

    def cmd_title(self, client, mess_data):
        """change room's subject

        @command (group): title
            - title: new room subject
        """
        subject = mess_data["unparsed"].strip()

        if subject:
            room = mess_data["to"]
            self.subject(client, room, subject)

        return False

    def cmd_topic(self, client, mess_data):
        """just a synonym of /title

        @command (group): title
            - title: new room subject
        """
        return self.cmd_title(client, mess_data)

    def cmd_list(self, client, mess_data):
        """list available rooms in a muc server

        @command (all): [MUC_SERVICE]
            - MUC_SERVICE: service to request
               empty value will request room's service for a room,
               or user's server default MUC service in a one2one chat
        """
        unparsed = mess_data["unparsed"].strip()
        try:
            service = jid.JID(unparsed)
        except RuntimeError:
            if mess_data['type'] == C.MESS_TYPE_GROUPCHAT:
                room_jid = mess_data["to"]
                service = jid.JID(room_jid.host)
            elif client.muc_service is not None:
                service = client.muc_service
            else:
                msg = D_(u"No known default MUC service".format(unparsed))
                self.text_cmds.feedBack(client, msg, mess_data)
                return False
        except jid.InvalidFormat:
            msg = D_(u"{} is not a valid JID!".format(unparsed))
            self.text_cmds.feedBack(client, msg, mess_data)
            return False
        d = self.host.getDiscoItems(client, service)
        d.addCallback(self._showListUI, client, service)

        return False

    def _whois(self, client, whois_msg, mess_data, target_jid):
        """ Add MUC user information to whois """
        if mess_data['type'] != "groupchat":
            return
        if target_jid.userhostJID() not in client._muc_client.joined_rooms:
            log.warning(_("This room has not been joined"))
            return
        if not target_jid.resource:
            return
        user = client._muc_client.joined_rooms[target_jid.userhostJID()].getUser(target_jid.resource)
        whois_msg.append(_("Nickname: %s") % user.nick)
        if user.entity:
            whois_msg.append(_("Entity: %s") % user.entity)
        if user.affiliation != 'none':
            whois_msg.append(_("Affiliation: %s") % user.affiliation)
        if user.role != 'none':
            whois_msg.append(_("Role: %s") % user.role)
        if user.status:
            whois_msg.append(_("Status: %s") % user.status)
        if user.show:
            whois_msg.append(_("Show: %s") % user.show)

    def presenceTrigger(self, presence_elt, client):
        # XXX: shouldn't it be done by the server ?!!
        muc_client = client._muc_client
        for room_jid, room in muc_client.joined_rooms.iteritems():
            elt = xml_tools.elementCopy(presence_elt)
            elt['to'] = room_jid.userhost() + '/' + room.nick
            client.presence.send(elt)
        return True

    def presenceReceivedTrigger(self, client, entity, show, priority, statuses):
        entity_bare = entity.userhostJID()
        muc_client = client._muc_client
        if entity_bare in muc_client.joined_rooms:
            room = muc_client.joined_rooms[entity_bare]
            if hasattr(room, "_cache_presence"):
                # room has a cache for presence, meaning it has not been fully
                # joined yet. So we put presence in cache, and stop workflow.
                # Or delete current presence and continue workflow if it's an
                # "unavailable" presence
                cache = room._cache_presence
                if show == C.PRESENCE_UNAVAILABLE:
                    try:
                        del cache[entity]
                    except KeyError:
                        pass
                    return True
                else:
                    cache[entity] = {
                        "entity": entity,
                        "show": show,
                        "statuses": statuses,
                        "priority": priority}
                    return False
        return True


class SatMUCClient(muc.MUCClient):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        muc.MUCClient.__init__(self)
        self._changing_nicks = set()  # used to keep trace of who is changing nick,
                                      # and to discard userJoinedRoom signal in this case
        print "init SatMUCClient OK"

    @property
    def joined_rooms(self):
        return self._rooms

    @property
    def host(self):
        return self.plugin_parent.host

    @property
    def client(self):
        return self.parent

    @property
    def _mam(self):
        return self.plugin_parent._mam

    @property
    def _si(self):
        return self.plugin_parent._si

    def changeRoomState(self, room, new_state):
        """Check that room is in expected state, and change it

        @param new_state: one of ROOM_STATE_*
        """
        new_state_idx = ROOM_STATES.index(new_state)
        if new_state_idx == -1:
            raise exceptions.InternalError("unknown room state")
        if new_state_idx < 1:
            raise exceptions.InternalError("unexpected new room state ({room}): {state}".format(
                room=room.userhost(),
                state=new_state))
        expected_state = ROOM_STATES[new_state_idx-1]
        if room.state != expected_state:
            log.error(_(
                u"room {room} is not in expected state: room is in state {current_state} "
                u"while we were expecting {expected_state}").format(
                room=room.userhost(),
                current_state=room.state,
                expected_state=expected_state))
        room.state = new_state

    def _addRoom(self, room):
        super(SatMUCClient, self)._addRoom(room)
        room._roster_ok = False  # True when occupants list has been fully received
        room.state = ROOM_STATE_OCCUPANTS
        # FIXME: check if history_d is not redundant with fully_joined
        room.fully_joined = defer.Deferred()  # called when everything is OK
        # cache data until room is ready
        # list of elements which will be re-injected in stream
        room._cache = []
        # we only need to keep last presence status for each jid, so a dict is suitable
        room._cache_presence = {}

    @defer.inlineCallbacks
    def _joinLegacy(self, client, room_jid, nick, password):
        """Join room an retrieve history with legacy method"""
        mess_data_list = yield self.host.memory.historyGet(room_jid,
                                                           client.jid.userhostJID(),
                                                           limit=1,
                                                           between=True,
                                                           profile=client.profile)
        if mess_data_list:
            timestamp = mess_data_list[0][1]
            # we use seconds since last message to get backlog without duplicates
            # and we remove 1 second to avoid getting the last message again
            seconds = int(time.time() - timestamp) - 1
        else:
            seconds = None

        room = yield super(SatMUCClient, self).join(
            room_jid, nick, muc.HistoryOptions(seconds=seconds), password)
        # used to send bridge signal once backlog are written in history
        room._history_type = HISTORY_LEGACY
        room._history_d = defer.Deferred()
        room._history_d.callback(None)
        defer.returnValue(room)

    @defer.inlineCallbacks
    def _joinMAM(self, client, room_jid, nick, password):
        """Join room and retrieve history using MAM"""
        room = yield super(SatMUCClient, self).join(
            # we don't want any history from room as we'll get it with MAM
            room_jid, nick, muc.HistoryOptions(maxStanzas=0), password=password)
        room._history_type = HISTORY_MAM
        room._history_d = defer.Deferred()

        last_mess = yield self.host.memory.historyGet(
            room_jid,
            None,
            limit=1,
            between=False,
            filters={
                u'types': C.MESS_TYPE_GROUPCHAT,
                u'last_stanza_id': True},
            profile=client.profile)
        if last_mess:
            stanza_id = last_mess[0][-1][u'stanza_id']
            rsm_req = rsm.RSMRequest(max_=100, after=stanza_id)
            no_loop=False
        else:
            log.info(u"We have no MAM archive for room {room_jid}.".format(
                room_jid=room_jid))
            # we don't want the whole archive if we have no archive yet
            # as it can be huge
            rsm_req = rsm.RSMRequest(max_=50, before=u'')
            no_loop=True

        mam_req = mam.MAMRequest(rsm_=rsm_req)
        complete = False
        count = 0
        while not complete:
            mam_data = yield self._mam.getArchives(client, mam_req,
                                                   service=room_jid)
            elt_list, rsm_response, mam_response = mam_data
            complete = True if no_loop else mam_response[u"complete"]
            # we update MAM request for next iteration
            mam_req.rsm.after = rsm_response.last

            if not elt_list:
                break
            else:
                count += len(elt_list)

                for mess_elt in elt_list:
                    try:
                        fwd_message_elt = self._mam.getMessageFromResult(
                            client, mess_elt, mam_req, service=room_jid)
                    except exceptions.DataError:
                        continue
                    if fwd_message_elt.getAttribute(u"to"):
                        log.warning(
                            u'Forwarded message element has a "to" attribute while it is '
                            u'forbidden by specifications')
                    fwd_message_elt[u"to"] = client.jid.full()
                    mess_data = client.messageProt.parseMessage(fwd_message_elt)
                    # we attache parsed message data to element, to avoid parsing
                    # again in _addToHistory
                    fwd_message_elt._mess_data = mess_data
                    # and we inject to MUC workflow
                    client._muc_client._onGroupChat(fwd_message_elt)

        if not count:
            log.info(_(u"No message received while offline in {room_jid}".format(
                room_jid=room_jid)))
        else:
            log.info(
                _(u"We have received {num_mess} message(s) in {room_jid} while "
                  u"offline.")
                .format(num_mess=count, room_jid=room_jid))

        # for legacy history, the following steps are done in receivedSubject but for MAM
        # the order is different (we have to join then get MAM archive, so subject
        # is received before archive), so we change state and add the callbacks here.
        self.changeRoomState(room, ROOM_STATE_LIVE)
        room._history_d.addCallbacks(self._historyCb, self._historyEb, [room],
                                     errbackArgs=[room])

        # callback is done now that all needed Deferred have been added to _history_d
        room._history_d.callback(None)

        defer.returnValue(room)

    @defer.inlineCallbacks
    def join(self, room_jid, nick, password=None):
        room_service = jid.JID(room_jid.host)
        has_mam = yield self.host.hasFeature(self.client, mam.NS_MAM, room_service)
        if not self._mam or not has_mam:
            room = yield self._joinLegacy(self.client, room_jid, nick, password)
            defer.returnValue(room)
        else:
            room = yield self._joinMAM(self.client, room_jid, nick, password)
            defer.returnValue(room)

    ## presence/roster ##

    def availableReceived(self, presence):
        """
        Available presence was received.
        """
        # XXX: we override MUCClient.availableReceived to fix bugs
        # (affiliation and role are not set)

        room, user = self._getRoomUser(presence)

        if room is None:
            return

        if user is None:
            nick = presence.sender.resource
            if not nick:
                log.warning(_(u"missing nick in presence: {xml}").format(
                    xml = presence.toElement().toXml()))
                return
            user = muc.User(nick, presence.entity)

        # Update user data
        user.role = presence.role
        user.affiliation = presence.affiliation
        user.status = presence.status
        user.show = presence.show

        if room.inRoster(user):
            self.userUpdatedStatus(room, user, presence.show, presence.status)
        else:
            room.addUser(user)
            self.userJoinedRoom(room, user)

    def unavailableReceived(self, presence):
        # XXX: we override this method to manage nickname change
        """
        Unavailable presence was received.

        If this was received from a MUC room occupant JID, that occupant has
        left the room.
        """
        room, user = self._getRoomUser(presence)

        if room is None or user is None:
            return

        room.removeUser(user)

        if muc.STATUS_CODE.NEW_NICK in presence.mucStatuses:
            self._changing_nicks.add(presence.nick)
            self.userChangedNick(room, user, presence.nick)
        else:
            self._changing_nicks.discard(presence.nick)
            self.userLeftRoom(room, user)

    def userJoinedRoom(self, room, user):
        if user.nick == room.nick:
            # we have received our own nick, this mean that the full room roster was received
            self.changeRoomState(room, ROOM_STATE_SELF_PRESENCE)
            log.debug(u"room {room} joined with nick {nick}".format(room=room.occupantJID.userhost(), nick=user.nick))
            # We set type so we don't have to use a deferred with disco to check entity type
            self.host.memory.updateEntityData(room.roomJID, C.ENTITY_TYPE, ENTITY_TYPE_MUC, profile_key=self.client.profile)
        elif room.state not in (ROOM_STATE_OCCUPANTS, ROOM_STATE_LIVE):
            log.warning(u"Received user presence data in a room before its initialisation (current state: {state}),"
                "this is not standard! Ignoring it: {room} ({nick})".format(
                state=room.state,
                room=room.roomJID.userhost(),
                nick=user.nick))
            return
        else:
            if not room.fully_joined.called:
                return
            try:
                self._changing_nicks.remove(user.nick)
            except KeyError:
                # this is a new user
                log.debug(_(u"user {nick} has joined room {room_id}").format(nick=user.nick, room_id=room.occupantJID.userhost()))
                if not self.host.trigger.point("MUC user joined", room, user, self.client.profile):
                    return

                extra = {'info_type': ROOM_USER_JOINED,
                         'user_affiliation': user.affiliation,
                         'user_role': user.role,
                         'user_nick': user.nick
                         }
                if user.entity is not None:
                    extra['user_entity'] = user.entity.full()
                mess_data = {  # dict is similar to the one used in client.onMessage
                    "from": room.roomJID,
                    "to": self.client.jid,
                    "uid": unicode(uuid.uuid4()),
                    "message": {'': D_(u"=> {} has joined the room").format(user.nick)},
                    "subject": {},
                    "type": C.MESS_TYPE_INFO,
                    "extra": extra,
                    "timestamp": time.time(),
                }
                # FIXME: we disable presence in history as it's taking a lot of space
                #        while not indispensable. In the future an option may allow
                #        to re-enable it
                # self.client.messageAddToHistory(mess_data)
                self.client.messageSendToBridge(mess_data)


    def userLeftRoom(self, room, user):
        if not self.host.trigger.point("MUC user left", room, user, self.client.profile):
            return
        if user.nick == room.nick:
            # we left the room
            room_jid_s = room.roomJID.userhost()
            log.info(_(u"Room ({room}) left ({profile})").format(
                room = room_jid_s, profile = self.client.profile))
            self.host.memory.delEntityCache(room.roomJID, profile_key=self.client.profile)
            self.host.bridge.mucRoomLeft(room.roomJID.userhost(), self.client.profile)
        elif room.state != ROOM_STATE_LIVE:
            log.warning(u"Received user presence data in a room before its initialisation (current state: {state}),"
                "this is not standard! Ignoring it: {room} ({nick})".format(
                state=room.state,
                room=room.roomJID.userhost(),
                nick=user.nick))
            return
        else:
            if not room.fully_joined.called:
                return
            log.debug(_(u"user {nick} left room {room_id}").format(nick=user.nick, room_id=room.occupantJID.userhost()))
            extra = {'info_type': ROOM_USER_LEFT,
                     'user_affiliation': user.affiliation,
                     'user_role': user.role,
                     'user_nick': user.nick
                     }
            if user.entity is not None:
                extra['user_entity'] = user.entity.full()
            mess_data = {  # dict is similar to the one used in client.onMessage
                "from": room.roomJID,
                "to": self.client.jid,
                "uid": unicode(uuid.uuid4()),
                "message": {'': D_(u"<= {} has left the room").format(user.nick)},
                "subject": {},
                "type": C.MESS_TYPE_INFO,
                "extra": extra,
                "timestamp": time.time(),
            }
            # FIXME: disable history, see userJoinRoom comment
            # self.client.messageAddToHistory(mess_data)
            self.client.messageSendToBridge(mess_data)

    def userChangedNick(self, room, user, new_nick):
        self.host.bridge.mucRoomUserChangedNick(room.roomJID.userhost(), user.nick, new_nick, self.client.profile)

    def userUpdatedStatus(self, room, user, show, status):
        self.host.bridge.presenceUpdate(room.roomJID.userhost() + '/' + user.nick, show or '', 0, {C.PRESENCE_STATUSES_DEFAULT: status or ''}, self.client.profile)

    ## messages ##

    def receivedGroupChat(self, room, user, body):
        log.debug(u'receivedGroupChat: room=%s user=%s body=%s' % (room.roomJID.full(), user, body))

    def _addToHistory(self, __, user, message):
        try:
            # message can be already parsed (with MAM), in this case mess_data
            # it attached to the element
            mess_data = message.element._mess_data
        except AttributeError:
            mess_data = self.client.messageProt.parseMessage(message.element)
        if mess_data[u'message'] or mess_data[u'subject']:
            return self.host.memory.addToHistory(self.client, mess_data)
        else:
            return defer.succeed(None)

    def _addToHistoryEb(self, failure):
        failure.trap(exceptions.CancelError)

    def receivedHistory(self, room, user, message):
        """Called when history (backlog) message are received

        we check if message is not already in our history
        and add it if needed
        @param room(muc.Room): room instance
        @param user(muc.User, None): the user that sent the message
            None if the message come from the room
        @param message(muc.GroupChat): the parsed message
        """
        if room.state != ROOM_STATE_SELF_PRESENCE:
            log.warning(_(
                u"received history in unexpected state in room {room} (state: "
                u"{state})").format(room = room.roomJID.userhost(),
                                    state = room.state))
            if not hasattr(room, "_history_d"):
                # XXX: this hack is due to buggy behaviour seen in the wild because of the
                #      "mod_delay" prosody module being activated. This module add an
                #      unexpected <delay> elements which break our workflow.
                log.warning(_(u"storing the unexpected message anyway, to avoid loss"))
                # we have to restore URI which are stripped by wokkel parsing
                for c in message.element.children:
                    if c.uri is None:
                        c.uri = C.NS_CLIENT
                mess_data = self.client.messageProt.parseMessage(message.element)
                message.element._mess_data = mess_data
                self._addToHistory(None, user, message)
                if mess_data[u'message'] or mess_data[u'subject']:
                    self.host.bridge.messageNew(
                        *self.client.messageGetBridgeArgs(mess_data),
                        profile=self.client.profile
                    )
                return
        room._history_d.addCallback(self._addToHistory, user, message)
        room._history_d.addErrback(self._addToHistoryEb)

    ## subject ##

    def groupChatReceived(self, message):
        """
        A group chat message has been received from a MUC room.

        There are a few event methods that may get called here.
        L{receivedGroupChat}, L{receivedSubject} or L{receivedHistory}.
        """
        # We override this method to fix subject handling
        # FIXME: remove this merge fixed upstream
        room, user = self._getRoomUser(message)

        if room is None:
            return

        if message.subject is not None:
            self.receivedSubject(room, user, message.subject)
        elif message.delay is None:
            self.receivedGroupChat(room, user, message)
        else:
            self.receivedHistory(room, user, message)

    def subject(self, room, subject):
        return muc.MUCClientProtocol.subject(self, room, subject)

    def _historyCb(self, __, room):
        """Called when history have been written to database and subject is received

        this method will finish joining by:
            - sending message to bridge
            - calling fully_joined deferred
            - sending stanza put in cache
            - cleaning variables not needed anymore
        """
        args = self.plugin_parent._getRoomJoinedArgs(room, self.client.profile)
        self.host.bridge.mucRoomJoined(*args)
        room.fully_joined.callback(room)
        del room._history_d
        del room._history_type
        cache = room._cache
        del room._cache
        cache_presence = room._cache_presence
        del room._cache_presence
        for elem in cache:
            self.client.xmlstream.dispatch(elem)
        for __, presence_data in cache_presence.iteritems():
            self.client.presence.availableReceived(**presence_data)

    def _historyEb(self, failure_, room):
        log.error(u"Error while managing history: {}".format(failure_))
        self._historyCb(None, room)

    def receivedSubject(self, room, user, subject):
        # when subject is received, we know that we have whole roster and history
        # cf. http://xmpp.org/extensions/xep-0045.html#enter-subject
        room.subject = subject  # FIXME: subject doesn't handle xml:lang
        if room.state != ROOM_STATE_LIVE:
            if room._history_type == HISTORY_LEGACY:
                self.changeRoomState(room, ROOM_STATE_LIVE)
                room._history_d.addCallbacks(self._historyCb, self._historyEb, [room], errbackArgs=[room])
        else:
            # the subject has been changed
            log.debug(_(u"New subject for room ({room_id}): {subject}").format(room_id = room.roomJID.full(), subject = subject))
            self.host.bridge.mucRoomNewSubject(room.roomJID.userhost(), subject, self.client.profile)

    ## disco ##

    def getDiscoInfo(self, requestor, target, nodeIdentifier=''):
        return [disco.DiscoFeature(NS_MUC)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=''):
        # TODO: manage room queries ? Bad for privacy, must be disabled by default
        #       see XEP-0045 § 6.7
        return []

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
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
from sat.tools.common import data_format
from sat.core import exceptions
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend.constants import Const as C
from collections import OrderedDict
from sat_frontends.tools import jid
import time
log = getLogger(__name__)

try:
    from locale import getlocale
except ImportError:
    # FIXME: pyjamas workaround
    getlocale = lambda x: (None, "utf-8")


ROOM_USER_JOINED = "ROOM_USER_JOINED"
ROOM_USER_LEFT = "ROOM_USER_LEFT"
ROOM_USER_MOVED = (ROOM_USER_JOINED, ROOM_USER_LEFT)

# from datetime import datetime

try:
    # FIXME: to be removed when an acceptable solution is here
    unicode("")  # XXX: unicode doesn't exist in pyjamas
except (
    TypeError,
    AttributeError,
):  # Error raised is not the same depending on pyjsbuild options
    unicode = str

# FIXME: day_format need to be settable (i18n)


class Message(object):
    """Message metadata"""

    def __init__(self, parent, uid, timestamp, from_jid, to_jid, msg, subject, type_,
                 extra, profile):
        self.parent = parent
        self.profile = profile
        self.uid = uid
        self.timestamp = timestamp
        self.from_jid = from_jid
        self.to_jid = to_jid
        self.message = msg
        self.subject = subject
        self.type = type_
        self.extra = extra
        self.nick = self.getNick(from_jid)
        self._status = None
        # own_mess is True if message was sent by profile's jid
        self.own_mess = (
            (from_jid.resource == self.parent.nick)
            if self.parent.type == C.CHAT_GROUP
            else (from_jid.bare == self.host.profiles[profile].whoami.bare)
        )
        # is user mentioned here ?
        if self.parent.type == C.CHAT_GROUP and not self.own_mess:
            for m in msg.itervalues():
                if self.parent.nick.lower() in m.lower():
                    self._mention = True
                    break
        self.handleMe()
        self.widgets = set()  # widgets linked to this message

    def __unicode__(self):
        return u"Message<{mess_type}>  [{time}]{nick}> {message}".format(
            mess_type=self.type,
            time=self.time_text,
            nick=self.nick,
            message=self.main_message)

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'ignore')

    @property
    def host(self):
        return self.parent.host

    @property
    def info_type(self):
        return self.extra.get("info_type")

    @property
    def mention(self):
        try:
            return self._mention
        except AttributeError:
            return False

    @property
    def history(self):
        """True if message come from history"""
        return self.extra.get("history", False)

    @property
    def main_message(self):
        """currently displayed message"""
        if self.parent.lang in self.message:
            self.selected_lang = self.parent.lang
            return self.message[self.parent.lang]
        try:
            self.selected_lang = ""
            return self.message[""]
        except KeyError:
            try:
                lang, mess = self.message.iteritems().next()
                self.selected_lang = lang
                return mess
            except StopIteration:
                log.error(u"Can't find message for uid {}".format(self.uid))
                return ""

    @property
    def main_message_xhtml(self):
        """rich message"""
        xhtml = {k: v for k, v in self.extra.iteritems() if "html" in k}
        if xhtml:
            # FIXME: we only return first found value for now
            return next(xhtml.itervalues())

    @property
    def time_text(self):
        """Return timestamp in a nicely formatted way"""
        # if the message was sent before today, we print the full date
        timestamp = time.localtime(self.timestamp)
        time_format = u"%c" if timestamp < self.parent.day_change else u"%H:%M"
        return time.strftime(time_format, timestamp).decode(getlocale()[1] or "utf-8")

    @property
    def avatar(self):
        """avatar full path or None if no avatar is found"""
        ret = self.host.getAvatar(self.from_jid, profile=self.profile)
        return ret

    def getNick(self, entity):
        """Return nick of an entity when possible"""
        contact_list = self.host.contact_lists[self.profile]
        if self.type == C.MESS_TYPE_INFO and self.info_type in ROOM_USER_MOVED:
            try:
                return self.extra["user_nick"]
            except KeyError:
                log.error(u"extra data is missing user nick for uid {}".format(self.uid))
                return ""
        # FIXME: converted getSpecials to list for pyjamas
        if self.parent.type == C.CHAT_GROUP or entity in list(
            contact_list.getSpecials(C.CONTACT_SPECIAL_GROUP)
        ):
            return entity.resource or ""
        if entity.bare in contact_list:
            return (
                contact_list.getCache(entity, "nick")
                or contact_list.getCache(entity, "name")
                or entity.node
                or entity
            )
        return entity.node or entity

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status != self._status:
            self._status = status
            for w in self.widgets:
                w.update({"status": status})

    def handleMe(self):
        """Check if messages starts with "/me " and change them if it is the case

        if several messages (different languages) are presents, they all need to start with "/me "
        """
        # TODO: XHTML-IM /me are not handled
        me = False
        # we need to check /me for every message
        for m in self.message.itervalues():
            if m.startswith(u"/me "):
                me = True
            else:
                me = False
                break
        if me:
            self.type = C.MESS_TYPE_INFO
            self.extra["info_type"] = "me"
            nick = self.nick
            for lang, mess in self.message.iteritems():
                self.message[lang] = u"* " + nick + mess[3:]


class MessageWidget(object):
    """Base classe for widgets"""
    # This class does nothing and is only used to have a common ancestor

    pass


class Occupant(object):
    """Occupant metadata"""

    def __init__(self, parent, data, profile):
        self.parent = parent
        self.profile = profile
        self.nick = data["nick"]
        self._entity = data.get("entity")
        self.affiliation = data["affiliation"]
        self.role = data["role"]
        self.widgets = set()  # widgets linked to this occupant
        self._state = None

    @property
    def data(self):
        """reconstruct data dict from attributes"""
        data = {}
        data["nick"] = self.nick
        if self._entity is not None:
            data["entity"] = self._entity
        data["affiliation"] = self.affiliation
        data["role"] = self.role
        return data

    @property
    def jid(self):
        """jid in the room"""
        return jid.JID(u"{}/{}".format(self.parent.target.bare, self.nick))

    @property
    def real_jid(self):
        """real jid if known else None"""
        return self._entity

    @property
    def host(self):
        return self.parent.host

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state != self._state:
            self._state = new_state
            for w in self.widgets:
                w.update({"state": new_state})

    def update(self, update_dict=None):
        for w in self.widgets:
            w.update(update_dict)


class QuickChat(quick_widgets.QuickWidget):
    visible_states = ["chat_state"]  # FIXME: to be removed, used only in quick_games

    def __init__(self, host, target, type_=C.CHAT_ONE2ONE, nick=None, occupants=None,
                 subject=None, profiles=None):
        """
        @param type_: can be C.CHAT_ONE2ONE for single conversation or C.CHAT_GROUP for
                      chat à la IRC
        """
        self.lang = ""  # default language to use for messages
        quick_widgets.QuickWidget.__init__(self, host, target, profiles=profiles)
        assert type_ in (C.CHAT_ONE2ONE, C.CHAT_GROUP)
        self.current_target = target
        self.type = type_
        self.encrypted = False  # True if this session is currently encrypted
        self._locked = False
        # True when resync is in progress, avoid resynchronising twice when resync is called
        # and history is still being updated. For internal use only
        self._resync_lock = False
        self.setLocked()
        if type_ == C.CHAT_GROUP:
            if target.resource:
                raise exceptions.InternalError(
                    u"a group chat entity can't have a resource"
                )
            if nick is None:
                raise exceptions.InternalError(u"nick must not be None for group chat")

            self.nick = nick
            self.occupants = {}
            self.setOccupants(occupants)
        else:
            if occupants is not None or nick is not None:
                raise exceptions.InternalError(
                    u"only group chat can have occupants or nick"
                )
        self.messages = OrderedDict()  # key: uid, value: Message instance
        self.games = {}  # key=game name (unicode), value=instance of quick_games.RoomGame
        self.subject = subject
        lt = time.localtime()
        self.day_change = (
            lt.tm_year,
            lt.tm_mon,
            lt.tm_mday,
            0,
            0,
            0,
            lt.tm_wday,
            lt.tm_yday,
            lt.tm_isdst,
        )  # struct_time of day changing time
        if self.host.AVATARS_HANDLER:
            self.host.addListener("avatar", self.onAvatar, profiles)

    def setLocked(self):
        """Set locked flag

        To be set when we are waiting for history/search
        """
        # FIXME: we don't use getter/setter here because of pyjamas
        # TODO: use proper getter/setter once we get rid of pyjamas
        if self._locked:
            log.warning(u"{wid} is already locked!".format(wid=self))
            return
        self._locked = True
        # messageNew signals are cached when locked
        self._cache = OrderedDict()
        log.debug(u"{wid} is now locked".format(wid=self))

    def setUnlocked(self):
        if not self._locked:
            log.debug(u"{wid} was already unlocked".format(wid=self))
            return
        self._locked = False
        for uid, data in self._cache.iteritems():
            if uid not in self.messages:
                self.messageNew(*data)
            else:
                log.debug(u"discarding message already in history: {data}, ".format(data=data))
        del self._cache
        log.debug(u"{wid} is now unlocked".format(wid=self))

    def postInit(self):
        """Method to be called by frontend after widget is initialised

        handle the display of history and subject
        """
        self.historyPrint(profile=self.profile)
        if self.subject is not None:
            self.setSubject(self.subject)
        if self.host.ENCRYPTION_HANDLERS:
            self.getEncryptionState()

    def onDelete(self):
        if self.host.AVATARS_HANDLER:
            self.host.removeListener("avatar", self.onAvatar)

    @property
    def contact_list(self):
        return self.host.contact_lists[self.profile]

    @property
    def message_widgets_rev(self):
        """Return the history of MessageWidget in reverse chronological order

        Must be implemented by frontend
        """
        raise NotImplementedError

    ## synchornisation handling ##

    @quick_widgets.QuickWidget.sync.setter
    def sync(self, state):
        quick_widgets.QuickWidget.sync.fset(self, state)
        if not state:
            self.setLocked()

    def _resyncComplete(self):
        self.sync = True
        self._resync_lock = False

    def resync(self):
        if self._resync_lock:
            return
        self._resync_lock = True
        log.debug(u"resynchronising {self}".format(self=self))
        for mess in reversed(self.messages.values()):
            if mess.type == C.MESS_TYPE_INFO:
                continue
            last_message = mess
            break
        else:
            # we have no message yet, we can get normal history
            self.historyPrint(callback=self._resyncComplete, profile=self.profile)
            return
        if self.type == C.CHAT_GROUP:
            self.occupants.clear()
            self.host.bridge.mucOccupantsGet(
                unicode(self.target), self.profile, callback=self.updateOccupants,
                errback=log.error)
        self.historyPrint(
            size=C.HISTORY_LIMIT_NONE,
            filters={'timestamp_start': last_message.timestamp},
            callback=self._resyncComplete,
            profile=self.profile)

    ## Widget management ##

    def __unicode__(self):
        return u"Chat Widget [target: {}, type: {}, profile: {}]".format(
            self.target, self.type, self.profile
        )

    @staticmethod
    def getWidgetHash(target, profiles):
        profile = list(profiles)[0]
        return profile + "\n" + unicode(target.bare)

    @staticmethod
    def getPrivateHash(target, profile):
        """Get unique hash for private conversations

        This method should be used with force_hash to get unique widget for private MUC conversations
        """
        return (unicode(profile), target)

    def addTarget(self, target):
        super(QuickChat, self).addTarget(target)
        if target.resource:
            self.current_target = (
                target
            )  # FIXME: tmp, must use resource priority throught contactList instead

    def recreateArgs(self, args, kwargs):
        """copy important attribute for a new widget"""
        kwargs["type_"] = self.type
        if self.type == C.CHAT_GROUP:
            kwargs["occupants"] = {o.nick: o.data for o in self.occupants.itervalues()}
        kwargs["subject"] = self.subject
        try:
            kwargs["nick"] = self.nick
        except AttributeError:
            pass

    def onPrivateCreated(self, widget):
        """Method called when a new widget for private conversation (MUC) is created"""
        raise NotImplementedError

    def getOrCreatePrivateWidget(self, entity):
        """Create a widget for private conversation, or get it if it already exists

        @param entity: full jid of the target
        """
        return self.host.widgets.getOrCreateWidget(
            QuickChat,
            entity,
            type_=C.CHAT_ONE2ONE,
            force_hash=self.getPrivateHash(self.profile, entity),
            on_new_widget=self.onPrivateCreated,
            profile=self.profile,
        )  # we force hash to have a new widget, not this one again

    @property
    def target(self):
        if self.type == C.CHAT_GROUP:
            return self.current_target.bare
        return self.current_target

    ## occupants ##

    def setOccupants(self, occupants):
        """Set the whole list of occupants"""
        assert len(self.occupants) == 0
        for nick, data in occupants.iteritems():
            log.debug(u"adding occupant {nick} to {room}".format(
                nick=nick, room=self.target))
            self.occupants[nick] = Occupant(self, data, self.profile)

    def updateOccupants(self, occupants):
        """Update occupants list

        In opposition to setOccupants, this only add missing occupants and remove
        occupants who have left
        """
        # FIXME: occupants with modified status are not handled
        local_occupants = set(self.occupants)
        updated_occupants = set(occupants)
        left_occupants = local_occupants - updated_occupants
        joined_occupants = updated_occupants - local_occupants
        log.debug(u"updating occupants for {room}:\n"
                  u"left: {left_occupants}\n"
                  u"joined: {joined_occupants}"
                  .format(room=self.target,
                          left_occupants=u", ".join(left_occupants),
                          joined_occupants=u", ".join(joined_occupants)))
        for nick in left_occupants:
            self.removeUser(occupants[nick])
        for nick in joined_occupants:
            self.addUser(occupants[nick])

    def addUser(self, occupant_data):
        """Add user if it is not in the group list"""
        occupant = Occupant(self, occupant_data, self.profile)
        self.occupants[occupant.nick] = occupant
        return occupant

    def removeUser(self, occupant_data):
        """Remove a user from the group list"""
        nick = occupant_data["nick"]
        try:
            occupant = self.occupants.pop(nick)
        except KeyError:
            log.warning(u"Trying to remove an unknown occupant: {}".format(nick))
        else:
            return occupant

    def setUserNick(self, nick):
        """Set the nick of the user, usefull for e.g. change the color of the user"""
        self.nick = nick

    def changeUserNick(self, old_nick, new_nick):
        """Change nick of a user in group list"""
        log.info("{old} is now known as {new} in room {room_jid}".format(
            old = old_nick,
            new = new_nick,
            room_jid = self.target))

    ## Messages ##

    def manageMessage(self, entity, mess_type):
        """Tell if this chat widget manage an entity and message type couple

        @param entity (jid.JID): (full) jid of the sending entity
        @param mess_type (str): message type as given by messageNew
        @return (bool): True if this Chat Widget manage this couple
        """
        if self.type == C.CHAT_GROUP:
            if (
                mess_type in (C.MESS_TYPE_GROUPCHAT, C.MESS_TYPE_INFO)
                and self.target == entity.bare
            ):
                return True
        else:
            if mess_type != C.MESS_TYPE_GROUPCHAT and entity in self.targets:
                return True
        return False

    def updateHistory(self, size=C.HISTORY_LIMIT_DEFAULT, filters=None, profile="@NONE@"):
        """Called when history need to be recreated

        Remove all message from history then call historyPrint
        Must probably be overriden by frontend to clear widget
        @param size (int): number of messages
        @param filters (str): patterns to filter the history results
        @param profile (str): %(doc_profile)s
        """
        self.setLocked()
        self.messages.clear()
        self.historyPrint(size, filters, profile=profile)

    def _onHistoryPrinted(self):
        """Method called when history is printed (or failed)

        unlock the widget, and can be used to refresh or scroll down
        the focus after the history is printed
        """
        self.setUnlocked()

    def historyPrint(self, size=C.HISTORY_LIMIT_DEFAULT, filters=None, callback=None,
                     profile="@NONE@"):
        """Print the current history

        Note: self.setUnlocked will be called once history is printed
        @param size (int): number of messages
        @param search (str): pattern to filter the history results
        @param callback(callable, None): method to call when history has been printed
        @param profile (str): %(doc_profile)s
        """
        if filters is None:
            filters = {}
        if size == 0:
            log.debug(u"Empty history requested, skipping")
            self._onHistoryPrinted()
            return
        log_msg = _(u"now we print the history")
        if size != C.HISTORY_LIMIT_DEFAULT:
            log_msg += _(u" ({} messages)".format(size))
        log.debug(log_msg)

        if self.type == C.CHAT_ONE2ONE:
            special = self.host.contact_lists[self.profile].getCache(
                self.target, C.CONTACT_SPECIAL, create_if_not_found=True
            )
            if special == C.CONTACT_SPECIAL_GROUP:
                # we have a private conversation
                # so we need full jid for the history
                # (else we would get history from group itself)
                # and to filter out groupchat message
                target = self.target
                filters["not_types"] = C.MESS_TYPE_GROUPCHAT
            else:
                target = self.target.bare
        else:
            # groupchat
            target = self.target.bare
            # FIXME: info not handled correctly
            filters["types"] = C.MESS_TYPE_GROUPCHAT

        def _historyGetCb(history):
            # day_format = "%A, %d %b %Y"  # to display the day change
            # previous_day = datetime.now().strftime(day_format)
            # message_day = datetime.fromtimestamp(timestamp).strftime(self.day_format)
            # if previous_day != message_day:
            #     self.printDayChange(message_day)
            #     previous_day = message_day
            for data in history:
                uid, timestamp, from_jid, to_jid, message, subject, type_, extra = data
                from_jid = jid.JID(from_jid)
                to_jid = jid.JID(to_jid)
                # if ((self.type == C.CHAT_GROUP and type_ != C.MESS_TYPE_GROUPCHAT) or
                #    (self.type == C.CHAT_ONE2ONE and type_ == C.MESS_TYPE_GROUPCHAT)):
                #     continue
                extra["history"] = True
                self.messages[uid] = Message(
                    self,
                    uid,
                    timestamp,
                    from_jid,
                    to_jid,
                    message,
                    subject,
                    type_,
                    extra,
                    profile,
                )
            self._onHistoryPrinted()
            if callback is not None:
                callback()

        def _historyGetEb(err):
            log.error(_(u"Can't get history: {}").format(err))
            self._onHistoryPrinted()
            if callback is not None:
                callback()

        self.host.bridge.historyGet(
            unicode(self.host.profiles[profile].whoami.bare),
            unicode(target),
            size,
            True,
            {k: unicode(v) for k,v in filters.iteritems()},
            profile,
            callback=_historyGetCb,
            errback=_historyGetEb,
        )

    def messageEncryptionGetCb(self, session_data):
        if session_data:
            session_data = data_format.deserialise(session_data)
            self.messageEncryptionStarted(session_data)

    def messageEncryptionGetEb(self, failure_):
        log.error(_(u"Can't get encryption state: {reason}").format(reason=failure_))

    def getEncryptionState(self):
        """Retrieve encryption state with current target.

        Once state is retrieved, default messageEncryptionStarted will be called if
        suitable
        """
        if self.type == C.CHAT_GROUP:
            return
        self.host.bridge.messageEncryptionGet(unicode(self.target.bare), self.profile,
                                              callback=self.messageEncryptionGetCb,
                                              errback=self.messageEncryptionGetEb)


    def messageNew(self, uid, timestamp, from_jid, to_jid, msg, subject, type_, extra,
                   profile):
        if self._locked:
            self._cache[uid] = (
                uid,
                timestamp,
                from_jid,
                to_jid,
                msg,
                subject,
                type_,
                extra,
                profile,
            )
            return

        if not msg and not subject and type_ != C.MESS_TYPE_INFO:
            log.warning(u"Received an empty message for uid {}".format(uid))
            return

        if self.type == C.CHAT_GROUP:
            if to_jid.resource and type_ != C.MESS_TYPE_GROUPCHAT:
                # we have a private message, we forward it to a private conversation
                # widget
                chat_widget = self.getOrCreatePrivateWidget(to_jid)
                chat_widget.messageNew(
                    uid, timestamp, from_jid, to_jid, msg, subject, type_, extra, profile
                )
                return
            if type_ == C.MESS_TYPE_INFO:
                try:
                    info_type = extra["info_type"]
                except KeyError:
                    pass
                else:
                    user_data = {
                        k[5:]: v for k, v in extra.iteritems() if k.startswith("user_")
                    }
                    if info_type == ROOM_USER_JOINED:
                        self.addUser(user_data)
                    elif info_type == ROOM_USER_LEFT:
                        self.removeUser(user_data)

        message = Message(
            self, uid, timestamp, from_jid, to_jid, msg, subject, type_, extra, profile
        )
        self.messages[uid] = message

        if "received_timestamp" in extra:
            log.warning(u"Delayed message received after history, this should not happen")
        self.createMessage(message)

    def messageEncryptionStarted(self, session_data):
        self.encrypted = True
        log.debug(_(u"message encryption started with {target} using {encryption}").format(
            target=self.target, encryption=session_data[u'name']))

    def messageEncryptionStopped(self, session_data):
        self.encrypted = False
        log.debug(_(u"message encryption stopped with {target} (was using {encryption})")
                 .format(target=self.target, encryption=session_data[u'name']))

    def createMessage(self, message, append=False):
        """Must be implemented by frontend to create and show a new message widget

        This is only called on messageNew, not on history.
        You need to override historyPrint to handle the later
        @param message(Message): message data
        """
        raise NotImplementedError

    def isUserMoved(self, message):
        """Return True if message is a user left/joined message

        @param message(Message): message to check
        @return (bool): True is message is user moved info message
        """
        if message.type != C.MESS_TYPE_INFO:
            return False
        try:
            info_type = message.extra["info_type"]
        except KeyError:
            return False
        else:
            return info_type in ROOM_USER_MOVED

    def handleUserMoved(self, message):
        """Check if this message is a UserMoved one, and merge it when possible

        "merge it" means that info message indicating a user joined/left will be
        grouped if no other non-info messages has been sent since
        @param message(Message): message to check
        @return (bool): True if this message has been merged
            if True, a new MessageWidget must not be created and appended to history
        """
        if self.isUserMoved(message):
            for wid in self.message_widgets_rev:
                # we merge in/out messages if no message was sent meanwhile
                if not isinstance(wid, MessageWidget):
                    continue
                elif wid.mess_data.type != C.MESS_TYPE_INFO:
                    return False
                elif (
                    wid.info_type in ROOM_USER_MOVED
                    and wid.mess_data.nick == message.nick
                ):
                    try:
                        count = wid.reentered_count
                    except AttributeError:
                        count = wid.reentered_count = 1
                    nick = wid.mess_data.nick
                    if message.info_type == ROOM_USER_LEFT:
                        wid.message = _(u"<= {nick} has left the room ({count})").format(
                            nick=nick, count=count
                        )
                    else:
                        wid.message = _(
                            u"<=> {nick} re-entered the room ({count})"
                        ).format(nick=nick, count=count)
                        wid.reentered_count += 1
                    return True
        return False

    def printDayChange(self, day):
        """Display the day on a new line.

        @param day(unicode): day to display (or not if this method is not overwritten)
        """
        # FIXME: not called anymore after refactoring
        pass

    ## Room ##

    def setSubject(self, subject):
        """Set title for a group chat"""
        if self.type != C.CHAT_GROUP:
            raise exceptions.InternalError(
                "trying to set subject for a non group chat window"
            )
        self.subject = subject

    def changeSubject(self, new_subject):
        """Change the subject of the room

        This change the subject on the room itself (i.e. via XMPP),
        while setSubject change the subject of this widget
        """
        self.host.bridge.mucSubject(unicode(self.target), new_subject, self.profile)

    def addGamePanel(self, widget):
        """Insert a game panel to this Chat dialog.

        @param widget (Widget): the game panel
        """
        raise NotImplementedError

    def removeGamePanel(self, widget):
        """Remove the game panel from this Chat dialog.

        @param widget (Widget): the game panel
        """
        raise NotImplementedError

    def update(self, entity=None):
        """Update one or all entities.

        @param entity (jid.JID): entity to update
        """
        # FIXME: to remove ?
        raise NotImplementedError

    ## events ##

    def onChatState(self, from_jid, state, profile):
        """A chat state has been received"""
        if self.type == C.CHAT_GROUP:
            nick = from_jid.resource
            try:
                self.occupants[nick].state = state
            except KeyError:
                log.warning(
                    u"{nick} not found in {room}, ignoring new chat state".format(
                        nick=nick, room=self.target.bare
                    )
                )

    def onMessageState(self, uid, status, profile):
        try:
            mess_data = self.messages[uid]
        except KeyError:
            pass
        else:
            mess_data.status = status

    def onAvatar(self, entity, filename, profile):
        if self.type == C.CHAT_GROUP:
            if entity.bare == self.target:
                try:
                    self.occupants[entity.resource].update({"avatar": filename})
                except KeyError:
                    # can happen for a message in history where the
                    # entity is not here anymore
                    pass

                for m in self.messages.values():
                    if m.nick == entity.resource:
                        for w in m.widgets:
                            w.update({"avatar": filename})
        else:
            if (
                entity.bare == self.target.bare
                or entity.bare == self.host.profiles[profile].whoami.bare
            ):
                log.info(u"avatar updated for {}".format(entity))
                for m in self.messages.values():
                    if m.from_jid.bare == entity.bare:
                        for w in m.widgets:
                            w.update({"avatar": filename})


quick_widgets.register(QuickChat)

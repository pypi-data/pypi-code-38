#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
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
from sat.core import log as logging

log = logging.getLogger(__name__)
import urwid
from urwid_satext import sat_widgets
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_chat
from sat_frontends.quick_frontend import quick_games
from sat_frontends.primitivus import game_tarot
from sat_frontends.primitivus.constants import Const as C
from sat_frontends.primitivus.keys import action_key_map as a_key
from sat_frontends.primitivus.widget import PrimitivusWidget
from sat_frontends.primitivus.contact_list import ContactList
from functools import total_ordering
import bisect


OCCUPANTS_FOOTER = _(u"{} occupants")


class MessageWidget(urwid.WidgetWrap, quick_chat.MessageWidget):
    def __init__(self, mess_data):
        """
        @param mess_data(quick_chat.Message, None): message data
            None: used only for non text widgets (e.g.: focus separator)
        """
        self.mess_data = mess_data
        mess_data.widgets.add(self)
        super(MessageWidget, self).__init__(urwid.Text(self.markup))

    @property
    def markup(self):
        return (
            self._generateInfoMarkup()
            if self.mess_data.type == C.MESS_TYPE_INFO
            else self._generateMarkup()
        )

    @property
    def info_type(self):
        return self.mess_data.info_type

    @property
    def parent(self):
        return self.mess_data.parent

    @property
    def message(self):
        """Return currently displayed message"""
        return self.mess_data.main_message

    @message.setter
    def message(self, value):
        self.mess_data.message = {"": value}
        self.redraw()

    @property
    def type(self):
        try:
            return self.mess_data.type
        except AttributeError:
            return C.MESS_TYPE_INFO

    def redraw(self):
        self._w.set_text(self.markup)
        self.mess_data.parent.host.redraw()  # FIXME: should not be necessary

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def get_cursor_coords(self, size):
        return 0, 0

    def render(self, size, focus=False):
        # Text widget doesn't render cursor, but we want one
        # so we add it here
        canvas = urwid.CompositeCanvas(self._w.render(size, focus))
        if focus:
            canvas.set_cursor(self.get_cursor_coords(size))
        return canvas

    def _generateInfoMarkup(self):
        return ("info_msg", self.message)

    def _generateMarkup(self):
        """Generate text markup according to message data and Widget options"""
        markup = []
        d = self.mess_data
        mention = d.mention

        # message status
        if d.status is None:
            markup.append(u" ")
        elif d.status == "delivered":
            markup.append(("msg_status_received", u"✔"))
        else:
            log.warning(u"Unknown status: {}".format(d.status))

        # timestamp
        if self.parent.show_timestamp:
            attr = "msg_mention" if mention else "date"
            markup.append((attr, u"[{}]".format(d.time_text)))
        else:
            if mention:
                markup.append(("msg_mention", "[*]"))

        # nickname
        if self.parent.show_short_nick:
            markup.append(
                ("my_nick" if d.own_mess else "other_nick", "**" if d.own_mess else "*")
            )
        else:
            markup.append(
                ("my_nick" if d.own_mess else "other_nick", u"[{}] ".format(d.nick or ""))
            )

        msg = self.message  # needed to generate self.selected_lang

        if d.selected_lang:
            markup.append(("msg_lang", u"[{}] ".format(d.selected_lang)))

        # message body
        markup.append(msg)

        return markup

    # events
    def update(self, update_dict=None):
        """update all the linked message widgets

        @param update_dict(dict, None): key=attribute updated value=new_value
        """
        self.redraw()


@total_ordering
class OccupantWidget(urwid.WidgetWrap):
    def __init__(self, occupant_data):
        self.occupant_data = occupant_data
        occupant_data.widgets.add(self)
        markup = self._generateMarkup()
        text = sat_widgets.ClickableText(markup)
        urwid.connect_signal(
            text,
            "click",
            self.occupant_data.parent._occupantsClicked,
            user_args=[self.occupant_data],
        )
        super(OccupantWidget, self).__init__(text)

    def __eq__(self, other):
        if other is None:
            return False
        return self.occupant_data.nick == other.occupant_data.nick

    def __lt__(self, other):
        return self.occupant_data.nick.lower() < other.occupant_data.nick.lower()

    @property
    def markup(self):
        return self._generateMarkup()

    @property
    def parent(self):
        return self.mess_data.parent

    @property
    def nick(self):
        return self.occupant_data.nick

    def redraw(self):
        self._w.set_text(self.markup)
        self.occupant_data.parent.host.redraw()  # FIXME: should not be necessary

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def get_cursor_coords(self, size):
        return 0, 0

    def render(self, size, focus=False):
        # Text widget doesn't render cursor, but we want one
        # so we add it here
        canvas = urwid.CompositeCanvas(self._w.render(size, focus))
        if focus:
            canvas.set_cursor(self.get_cursor_coords(size))
        return canvas

    def _generateMarkup(self):
        # TODO: role and affiliation are shown in a Q&D way
        #       should be more intuitive and themable
        o = self.occupant_data
        markup = []
        markup.append(
            ("info_msg", u"{}{} ".format(o.role[0].upper(), o.affiliation[0].upper()))
        )
        markup.append(o.nick)
        if o.state is not None:
            markup.append(u" {}".format(C.CHAT_STATE_ICON[o.state]))
        return markup

    # events
    def update(self, update_dict=None):
        self.redraw()


class OccupantsWidget(urwid.WidgetWrap):
    def __init__(self, parent):
        self.parent = parent
        self.occupants_walker = urwid.SimpleListWalker([])
        self.occupants_footer = urwid.Text("", align="center")
        self.updateFooter()
        occupants_widget = urwid.Frame(
            urwid.ListBox(self.occupants_walker), footer=self.occupants_footer
        )
        super(OccupantsWidget, self).__init__(occupants_widget)
        occupants_list = sorted(self.parent.occupants.keys(), key=lambda o: o.lower())
        for occupant in occupants_list:
            occupant_data = self.parent.occupants[occupant]
            self.occupants_walker.append(OccupantWidget(occupant_data))

    def updateFooter(self):
        """update footer widget"""
        txt = OCCUPANTS_FOOTER.format(len(self.parent.occupants))
        self.occupants_footer.set_text(txt)

    def getNicks(self, start=u""):
        """Return nicks of all occupants

        @param start(unicode): only return nicknames which start with this text
        """
        return [
            w.nick
            for w in self.occupants_walker
            if isinstance(w, OccupantWidget) and w.nick.startswith(start)
        ]

    def addUser(self, occupant_data):
        """add a user to the list"""
        bisect.insort(self.occupants_walker, OccupantWidget(occupant_data))
        self.updateFooter()
        self.parent.host.redraw()  # FIXME: should not be necessary

    def removeUser(self, occupant_data):
        """remove a user from the list"""
        for widget in occupant_data.widgets:
            self.occupants_walker.remove(widget)
        self.updateFooter()
        self.parent.host.redraw()  # FIXME: should not be necessary


class Chat(PrimitivusWidget, quick_chat.QuickChat):
    def __init__(self, host, target, type_=C.CHAT_ONE2ONE, nick=None, occupants=None,
                 subject=None, profiles=None):
        quick_chat.QuickChat.__init__(
            self, host, target, type_, nick, occupants, subject, profiles=profiles
        )
        self.filters = []  # list of filter callbacks to apply
        self.mess_walker = urwid.SimpleListWalker([])
        self.mess_widgets = urwid.ListBox(self.mess_walker)
        self.chat_widget = urwid.Frame(self.mess_widgets)
        self.chat_colums = urwid.Columns([("weight", 8, self.chat_widget)])
        self.pile = urwid.Pile([self.chat_colums])
        PrimitivusWidget.__init__(self, self.pile, self.target)

        # we must adapt the behaviour with the type
        if type_ == C.CHAT_GROUP:
            if len(self.chat_colums.contents) == 1:
                self.occupants_widget = OccupantsWidget(self)
                self.occupants_panel = sat_widgets.VerticalSeparator(
                    self.occupants_widget
                )
                self._appendOccupantsPanel()
                self.host.addListener("presence", self.presenceListener, [profiles])

        # focus marker is a separator indicated last visible message before focus was lost
        self.focus_marker = None  # link to current marker
        self.focus_marker_set = None  # True if a new marker has been inserted
        self.show_timestamp = True
        self.show_short_nick = False
        self.show_title = 1  # 0: clip title; 1: full title; 2: no title
        self.postInit()

    @property
    def message_widgets_rev(self):
        return reversed(self.mess_walker)

    def keypress(self, size, key):
        if key == a_key["OCCUPANTS_HIDE"]:  # user wants to (un)hide the occupants panel
            if self.type == C.CHAT_GROUP:
                widgets = [widget for (widget, options) in self.chat_colums.contents]
                if self.occupants_panel in widgets:
                    self._removeOccupantsPanel()
                else:
                    self._appendOccupantsPanel()
        elif key == a_key["TIMESTAMP_HIDE"]:  # user wants to (un)hide timestamp
            self.show_timestamp = not self.show_timestamp
            self.redraw()
        elif key == a_key["SHORT_NICKNAME"]:  # user wants to (not) use short nick
            self.show_short_nick = not self.show_short_nick
            self.redraw()
        elif (key == a_key["SUBJECT_SWITCH"]):
            # user wants to (un)hide group's subject or change its apperance
            if self.subject:
                self.show_title = (self.show_title + 1) % 3
                if self.show_title == 0:
                    self.setSubject(self.subject, "clip")
                elif self.show_title == 1:
                    self.setSubject(self.subject, "space")
                elif self.show_title == 2:
                    self.chat_widget.header = None
                self._invalidate()
        elif key == a_key["GOTO_BOTTOM"]:  # user wants to focus last message
            self.mess_widgets.focus_position = len(self.mess_walker) - 1

        return super(Chat, self).keypress(size, key)

    def completion(self, text, completion_data):
        """Completion method which complete nicknames in group chat

        for params, see [sat_widgets.AdvancedEdit]
        """
        if self.type != C.CHAT_GROUP:
            return text

        space = text.rfind(" ")
        start = text[space + 1 :]
        words = self.occupants_widget.getNicks(start)
        if not words:
            return text
        try:
            word_idx = words.index(completion_data["last_word"]) + 1
        except (KeyError, ValueError):
            word_idx = 0
        else:
            if word_idx == len(words):
                word_idx = 0
        word = completion_data["last_word"] = words[word_idx]
        return u"{}{}{}".format(text[: space + 1], word, ": " if space < 0 else "")

    def getMenu(self):
        """Return Menu bar"""
        menu = sat_widgets.Menu(self.host.loop)
        if self.type == C.CHAT_GROUP:
            self.host.addMenus(menu, C.MENU_ROOM, {"room_jid": self.target.bare})
            game = _("Game")
            menu.addMenu(game, "Tarot", self.onTarotRequest)
        elif self.type == C.CHAT_ONE2ONE:
            # FIXME: self.target is a bare jid, we need to check that
            contact_list = self.host.contact_lists[self.profile]
            if not self.target.resource:
                full_jid = contact_list.getFullJid(self.target)
            else:
                full_jid = self.target
            self.host.addMenus(menu, C.MENU_SINGLE, {"jid": full_jid})
        return menu

    def setFilter(self, args):
        """set filtering of messages

        @param args(list[unicode]): filters following syntax "[filter]=[value]"
            empty list to clear all filters
            only lang=XX is handled for now
        """
        del self.filters[:]
        if args:
            if args[0].startswith("lang="):
                lang = args[0][5:].strip()
                self.filters.append(lambda mess_data: lang in mess_data.message)

        self.printMessages()

    def presenceListener(self, entity, show, priority, statuses, profile):
        """Update entity's presence status

        @param entity (jid.JID): entity updated
        @param show: availability
        @param priority: resource's priority
        @param statuses: dict of statuses
        @param profile: %(doc_profile)s
        """
        # FIXME: disable for refactoring, need to be checked and re-enabled
        return
        # assert self.type == C.CHAT_GROUP
        # if entity.bare != self.target:
        #     return
        # self.update(entity)

    def createMessage(self, message):
        self.appendMessage(message)

    def _scrollDown(self):
        """scroll down message only if we are already at the bottom (minus 1)"""
        current_focus = self.mess_widgets.focus_position
        bottom = len(self.mess_walker) - 1
        if current_focus == bottom - 1:
            self.mess_widgets.focus_position = bottom  # scroll down
        self.host.redraw()  # FIXME: should not be necessary

    def appendMessage(self, message):
        """Create a MessageWidget and append it

        Can merge messages together is desirable (e.g.: multiple joined/leave)
        @param message(quick_chat.Message): message to add
        """
        if self.filters:
            if not all([f(message) for f in self.filters]):
                return

        if self.handleUserMoved(message):
            return

        if ((self.host.selected_widget != self or not self.host.x_notify.hasFocus())
            and self.focus_marker_set is not None):
            if not self.focus_marker_set and not self._locked and self.mess_walker:
                if self.focus_marker is not None:
                    try:
                        self.mess_walker.remove(self.focus_marker)
                    except ValueError:
                        # self.focus_marker may not be in mess_walker anymore if
                        # mess_walker has been cleared, e.g. when showing search
                        # result or using :history command
                        pass
                self.focus_marker = urwid.Divider("—")
                self.mess_walker.append(self.focus_marker)
                self.focus_marker_set = True
                self._scrollDown()
        else:
            if self.focus_marker_set:
                self.focus_marker_set = False

        wid = MessageWidget(message)
        self.mess_walker.append(wid)
        self._scrollDown()
        if self.isUserMoved(message):
            return  # no notification for moved messages

        # notifications

        if self._locked:
            # we don't want notifications when locked
            # because that's history messages
            return

        if wid.mess_data.mention:
            from_jid = wid.mess_data.from_jid
            msg = _(
                u"You have been mentioned by {nick} in {room}".format(
                    nick=wid.mess_data.nick, room=self.target
                )
            )
            self.host.notify(
                C.NOTIFY_MENTION, from_jid, msg, widget=self, profile=self.profile
            )
        elif self.type == C.CHAT_ONE2ONE:
            from_jid = wid.mess_data.from_jid
            msg = _(u"{entity} is talking to you".format(entity=from_jid))
            self.host.notify(
                C.NOTIFY_MESSAGE, from_jid, msg, widget=self, profile=self.profile
            )
        else:
            self.host.notify(
                C.NOTIFY_MESSAGE, self.target, widget=self, profile=self.profile
            )

    def addUser(self, nick):
        occupant = super(Chat, self).addUser(nick)
        self.occupants_widget.addUser(occupant)

    def removeUser(self, occupant_data):
        occupant = super(Chat, self).removeUser(occupant_data)
        if occupant is not None:
            self.occupants_widget.removeUser(occupant)

    def _occupantsClicked(self, occupant, clicked_wid):
        assert self.type == C.CHAT_GROUP
        contact_list = self.host.contact_lists[self.profile]

        # we have a click on a nick, we need to create the widget if it doesn't exists
        self.getOrCreatePrivateWidget(occupant.jid)

        # now we select the new window
        for contact_list in self.host.widgets.getWidgets(
            ContactList, profiles=(self.profile,)
        ):
            contact_list.setFocus(occupant.jid, True)

    def _appendOccupantsPanel(self):
        self.chat_colums.contents.append((self.occupants_panel, ("weight", 2, False)))

    def _removeOccupantsPanel(self):
        for widget, options in self.chat_colums.contents:
            if widget is self.occupants_panel:
                self.chat_colums.contents.remove((widget, options))
                break

    def addGamePanel(self, widget):
        """Insert a game panel to this Chat dialog.

        @param widget (Widget): the game panel
        """
        assert len(self.pile.contents) == 1
        self.pile.contents.insert(0, (widget, ("weight", 1)))
        self.pile.contents.insert(1, (urwid.Filler(urwid.Divider("-"), ("fixed", 1))))
        self.host.redraw()

    def removeGamePanel(self, widget):
        """Remove the game panel from this Chat dialog.

        @param widget (Widget): the game panel
        """
        assert len(self.pile.contents) == 3
        del self.pile.contents[0]
        self.host.redraw()

    def setSubject(self, subject, wrap="space"):
        """Set title for a group chat"""
        quick_chat.QuickChat.setSubject(self, subject)
        self.subj_wid = urwid.Text(
            unicode(subject.replace("\n", "|") if wrap == "clip" else subject),
            align="left" if wrap == "clip" else "center",
            wrap=wrap,
        )
        self.chat_widget.header = urwid.AttrMap(self.subj_wid, "title")
        self.host.redraw()

    ## Messages

    def printMessages(self, clear=True):
        """generate message widgets

        @param clear(bool): clear message before printing if true
        """
        if clear:
            del self.mess_walker[:]
        for message in self.messages.itervalues():
            self.appendMessage(message)

    def redraw(self):
        """redraw all messages"""
        for w in self.mess_walker:
            try:
                w.redraw()
            except AttributeError:
                pass

    def updateHistory(self, size=C.HISTORY_LIMIT_DEFAULT, filters=None, profile="@NONE@"):
        del self.mess_walker[:]
        if filters and "search" in filters:
            self.mess_walker.append(
                urwid.Text(
                    _(u"Results for searching the globbing pattern: {}").format(
                        filters["search"]
                    )
                )
            )
            self.mess_walker.append(
                urwid.Text(_(u"Type ':history <lines>' to reset the chat history"))
            )
        super(Chat, self).updateHistory(size, filters, profile)

    def _onHistoryPrinted(self):
        """Refresh or scroll down the focus after the history is printed"""
        self.printMessages(clear=False)
        super(Chat, self)._onHistoryPrinted()

    def onPrivateCreated(self, widget):
        self.host.contact_lists[widget.profile].setSpecial(
            widget.target, C.CONTACT_SPECIAL_GROUP
        )

    def onSelected(self):
        self.focus_marker_set = False

    def notify(self, contact="somebody", msg=""):
        """Notify the user of a new message if primitivus doesn't have the focus.

        @param contact (unicode): contact who wrote to the users
        @param msg (unicode): the message that has been received
        """
        # FIXME: not called anymore after refactoring
        if msg == "":
            return
        if self.mess_widgets.get_focus()[1] == len(self.mess_walker) - 2:
            # we don't change focus if user is not at the bottom
            # as that mean that he is probably watching discussion history
            self.mess_widgets.focus_position = len(self.mess_walker) - 1
        self.host.redraw()
        if not self.host.x_notify.hasFocus():
            if self.type == C.CHAT_ONE2ONE:
                self.host.x_notify.sendNotification(
                    _("Primitivus: %s is talking to you") % contact
                )
            elif self.nick is not None and self.nick.lower() in msg.lower():
                self.host.x_notify.sendNotification(
                    _("Primitivus: %(user)s mentioned you in room '%(room)s'")
                    % {"user": contact, "room": self.target}
                )

    # MENU EVENTS #
    def onTarotRequest(self, menu):
        # TODO: move this to plugin_misc_tarot with dynamic menu
        if len(self.occupants) != 4:
            self.host.showPopUp(
                sat_widgets.Alert(
                    _("Can't start game"),
                    _(
                        "You need to be exactly 4 peoples in the room to start a Tarot game"
                    ),
                    ok_cb=self.host.removePopUp,
                )
            )
        else:
            self.host.bridge.tarotGameCreate(
                self.target, list(self.occupants), self.profile
            )

    # MISC EVENTS #

    def onDelete(self):
        # FIXME: to be checked after refactoring
        super(Chat, self).onDelete()
        if self.type == C.CHAT_GROUP:
            self.host.removeListener("presence", self.presenceListener)

    def onChatState(self, from_jid, state, profile):
        super(Chat, self).onChatState(from_jid, state, profile)
        if self.type == C.CHAT_ONE2ONE:
            self.title_dynamic = C.CHAT_STATE_ICON[state]
            self.host.redraw()  # FIXME: should not be necessary

    def _onSubjectDialogCb(self, button, dialog):
        self.changeSubject(dialog.text)
        self.host.removePopUp(dialog)

    def onSubjectDialog(self, new_subject=None):
        dialog = sat_widgets.InputDialog(
            _(u"Change title"),
            _(u"Enter the new title"),
            default_txt=new_subject if new_subject is not None else self.subject,
        )
        dialog.setCallback("ok", self._onSubjectDialogCb, dialog)
        dialog.setCallback("cancel", lambda __: self.host.removePopUp(dialog))
        self.host.showPopUp(dialog)


quick_widgets.register(quick_chat.QuickChat, Chat)
quick_widgets.register(quick_games.Tarot, game_tarot.TarotGame)

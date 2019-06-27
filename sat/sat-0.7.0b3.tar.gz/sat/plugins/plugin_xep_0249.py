#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0249
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
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid

from zope.interface import implements

from wokkel import disco, iwokkel


try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

MESSAGE = "/message"
NS_DIRECT_MUC_INVITATION = "jabber:x:conference"
DIRECT_MUC_INVITATION_REQUEST = MESSAGE + '/x[@xmlns="' + NS_DIRECT_MUC_INVITATION + '"]'
AUTOJOIN_KEY = "Misc"
AUTOJOIN_NAME = "Auto-join MUC on invitation"
AUTOJOIN_VALUES = ["ask", "always", "never"]

PLUGIN_INFO = {
    C.PI_NAME: "XEP 0249 Plugin",
    C.PI_IMPORT_NAME: "XEP-0249",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0249"],
    C.PI_DEPENDENCIES: ["XEP-0045"],
    C.PI_RECOMMENDATIONS: [C.TEXT_CMDS],
    C.PI_MAIN: "XEP_0249",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Direct MUC Invitations"""),
}


class XEP_0249(object):

    params = """
    <params>
    <individual>
    <category name="%(category_name)s" label="%(category_label)s">
        <param name="%(param_name)s" label="%(param_label)s" type="list" security="0">
            %(param_options)s
        </param>
     </category>
    </individual>
    </params>
    """ % {
        "category_name": AUTOJOIN_KEY,
        "category_label": _("Misc"),
        "param_name": AUTOJOIN_NAME,
        "param_label": _("Auto-join MUC on invitation"),
        "param_options": "\n".join(
            [
                '<option value="%s" %s/>'
                % (value, 'selected="true"' if value == AUTOJOIN_VALUES[0] else "")
                for value in AUTOJOIN_VALUES
            ]
        ),
    }

    def __init__(self, host):
        log.info(_("Plugin XEP_0249 initialization"))
        self.host = host
        host.memory.updateParams(self.params)
        host.bridge.addMethod(
            "inviteMUC", ".plugin", in_sign="ssa{ss}s", out_sign="", method=self._invite
        )
        try:
            self.host.plugins[C.TEXT_CMDS].registerTextCommands(self)
        except KeyError:
            log.info(_("Text commands not available"))

    def getHandler(self, client):
        return XEP_0249_handler(self)

    def _invite(self, guest_jid_s, room_jid_s, options, profile_key):
        """Invite an user to a room

        @param guest_jid_s: jid of the user to invite
        @param service: jid of the MUC service
        @param roomId: name of the room
        @param profile_key: %(doc_profile_key)s
        """
        # TODO: check parameters validity
        client = self.host.getClient(profile_key)
        self.invite(client, jid.JID(guest_jid_s), jid.JID(room_jid_s, options))

    def invite(self, client, guest, room, options={}):
        """Invite a user to a room

        @param guest(jid.JID): jid of the user to invite
        @param room(jid.JID): jid of the room where the user is invited
        @param options(dict): attribute with extra info (reason, password) as in #XEP-0249
        """
        message = domish.Element((None, "message"))
        message["to"] = guest.full()
        x_elt = message.addElement((NS_DIRECT_MUC_INVITATION, "x"))
        x_elt["jid"] = room.userhost()
        for key, value in options.iteritems():
            if key not in ("password", "reason", "thread"):
                log.warning(u"Ignoring invalid invite option: {}".format(key))
                continue
            x_elt[key] = value
        #  there is not body in this message, so we can use directly send()
        client.send(message)

    def _accept(self, room_jid, profile_key=C.PROF_KEY_NONE):
        """Accept the invitation to join a MUC.

        @param room (jid.JID): JID of the room
        """
        client = self.host.getClient(profile_key)
        log.info(
            _(u"Invitation accepted for room %(room)s [%(profile)s]")
            % {"room": room_jid.userhost(), "profile": client.profile}
        )
        d = self.host.plugins["XEP-0045"].join(client, room_jid, client.jid.user, {})
        return d

    def onInvitation(self, message, profile):
        """
        called when an invitation is received
        @param message: message element
        @profile: %(doc_profile)s
        """
        client = self.host.getClient(profile)
        try:
            room_jid_s = message.firstChildElement()["jid"]
            log.info(
                _(u"Invitation received for room %(room)s [%(profile)s]")
                % {"room": room_jid_s, "profile": profile}
            )
        except:
            log.error(_("Error while parsing invitation"))
            return
        from_jid_s = message["from"]
        room_jid = jid.JID(room_jid_s)
        try:
            self.host.plugins["XEP-0045"].checkRoomJoined(client, room_jid)
        except exceptions.NotFound:
            pass
        else:
            log.info(
                _(u"Invitation silently discarded because user is already in the room.")
            )
            return

        autojoin = self.host.memory.getParamA(
            AUTOJOIN_NAME, AUTOJOIN_KEY, profile_key=profile
        )

        if autojoin == "always":
            self._accept(room_jid, profile)
        elif autojoin == "never":
            msg = D_(
                "An invitation from %(user)s to join the room %(room)s has been declined according to your personal settings."
            ) % {"user": from_jid_s, "room": room_jid_s}
            title = D_("MUC invitation")
            xml_tools.quickNote(self.host, client, msg, title, C.XMLUI_DATA_LVL_INFO)
        else:  # leave the default value here
            confirm_msg = D_(
                "You have been invited by %(user)s to join the room %(room)s. Do you accept?"
            ) % {"user": from_jid_s, "room": room_jid_s}
            confirm_title = D_("MUC invitation")
            d = xml_tools.deferConfirm(
                self.host, confirm_msg, confirm_title, profile=profile
            )

            def accept_cb(accepted):
                if accepted:
                    self._accept(room_jid, profile)

            d.addCallback(accept_cb)

    def cmd_invite(self, client, mess_data):
        """invite someone in the room

        @command (group): JID
            - JID: the JID of the person to invite
        """
        contact_jid_s = mess_data["unparsed"].strip()
        my_host = client.jid.host
        try:
            contact_jid = jid.JID(contact_jid_s)
        except (RuntimeError, jid.InvalidFormat, AttributeError):
            feedback = _(
                u"You must provide a valid JID to invite, like in '/invite contact@{host}'"
            ).format(host=my_host)
            self.host.plugins[C.TEXT_CMDS].feedBack(client, feedback, mess_data)
            return False
        if not contact_jid.user:
            contact_jid.user, contact_jid.host = contact_jid.host, my_host
        self.invite(client, contact_jid, mess_data["to"])
        return False


class XEP_0249_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            DIRECT_MUC_INVITATION_REQUEST,
            self.plugin_parent.onInvitation,
            profile=self.parent.profile,
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_DIRECT_MUC_INVITATION)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

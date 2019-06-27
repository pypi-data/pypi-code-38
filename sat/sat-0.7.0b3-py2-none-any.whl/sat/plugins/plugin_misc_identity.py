#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0054
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2014 Emmanuel Gil Peyrot (linkmauve@linkmauve.fr)

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
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
import os.path


PLUGIN_INFO = {
    C.PI_NAME: "Identity Plugin",
    C.PI_IMPORT_NAME: "IDENTITY",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0054"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "Identity",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Identity manager"""),
}


class Identity(object):
    def __init__(self, host):
        log.info(_(u"Plugin Identity initialization"))
        self.host = host
        self._v = host.plugins[u"XEP-0054"]
        host.bridge.addMethod(
            u"identityGet",
            u".plugin",
            in_sign=u"ss",
            out_sign=u"a{ss}",
            method=self._getIdentity,
            async=True,
        )
        host.bridge.addMethod(
            u"identitySet",
            u".plugin",
            in_sign=u"a{ss}s",
            out_sign=u"",
            method=self._setIdentity,
            async=True,
        )

    def _getIdentity(self, jid_str, profile):
        jid_ = jid.JID(jid_str)
        client = self.host.getClient(profile)
        return self.getIdentity(client, jid_)

    @defer.inlineCallbacks
    def getIdentity(self, client, jid_):
        """Retrieve identity of an entity

        @param jid_(jid.JID): entity to check
        @return (dict(unicode, unicode)): identity data where key can be:
            - nick: nickname of the entity
                nickname is checked from, in this order:
                    roster, vCard, user part of jid
            cache is used when possible
        """
        id_data = {}
        # we first check roster
        roster_item = yield client.roster.getItem(jid_.userhostJID())
        if roster_item is not None and roster_item.name:
            id_data[u"nick"] = roster_item.name
        elif jid_.resource and self._v.isRoom(client, jid_):
            id_data[u"nick"] = jid_.resource
        else:
            #  and finally then vcard
            nick = yield self._v.getNick(client, jid_)
            if nick:
                id_data[u"nick"] = nick
            elif jid_.user:
                id_data[u"nick"] = jid_.user.capitalize()
            else:
                id_data[u"nick"] = jid_.userhost()

        try:
            avatar_path = id_data[u"avatar"] = yield self._v.getAvatar(
                client, jid_, cache_only=False
            )
        except exceptions.NotFound:
            pass
        else:
            if avatar_path:
                id_data[u"avatar_basename"] = os.path.basename(avatar_path)
            else:
                del id_data[u"avatar"]

        defer.returnValue(id_data)

    def _setIdentity(self, id_data, profile):
        client = self.host.getClient(profile)
        return self.setIdentity(client, id_data)

    def setIdentity(self, client, id_data):
        """Update profile's identity

        @param id_data(dict[unicode, unicode]): data to update, key can be:
            - nick: nickname
                the vCard will be updated
        """
        if id_data.keys() != [u"nick"]:
            raise NotImplementedError(u"Only nick can be updated for now")
        if u"nick" in id_data:
            return self._v.setNick(client, id_data[u"nick"])

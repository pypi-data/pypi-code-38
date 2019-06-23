#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing gateways (xep-0100)
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
from sat.tools import xml_tools
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.protocols.jabber import jid
from twisted.internet import reactor, defer

PLUGIN_INFO = {
    C.PI_NAME: "Gateways Plugin",
    C.PI_IMPORT_NAME: "XEP-0100",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0100"],
    C.PI_DEPENDENCIES: ["XEP-0077"],
    C.PI_MAIN: "XEP_0100",
    C.PI_DESCRIPTION: _("""Implementation of Gateways protocol"""),
}

WARNING_MSG = D_(
    u"""Be careful ! Gateways allow you to use an external IM (legacy IM), so you can see your contact as XMPP contacts.
But when you do this, all your messages go throught the external legacy IM server, it is a huge privacy issue (i.e.: all your messages throught the gateway can be monitored, recorded, analysed by the external server, most of time a private company)."""
)

GATEWAY_TIMEOUT = 10  # time to wait before cancelling a gateway disco info, in seconds

TYPE_DESCRIPTIONS = {
    "irc": D_("Internet Relay Chat"),
    "xmpp": D_("XMPP"),
    "qq": D_("Tencent QQ"),
    "simple": D_("SIP/SIMPLE"),
    "icq": D_("ICQ"),
    "yahoo": D_("Yahoo! Messenger"),
    "gadu-gadu": D_("Gadu-Gadu"),
    "aim": D_("AOL Instant Messenger"),
    "msn": D_("Windows Live Messenger"),
}


class XEP_0100(object):
    def __init__(self, host):
        log.info(_("Gateways plugin initialization"))
        self.host = host
        self.__gateways = {}  # dict used to construct the answer to findGateways. Key = target jid
        host.bridge.addMethod(
            "findGateways",
            ".plugin",
            in_sign="ss",
            out_sign="s",
            method=self._findGateways,
        )
        host.bridge.addMethod(
            "gatewayRegister",
            ".plugin",
            in_sign="ss",
            out_sign="s",
            method=self._gatewayRegister,
        )
        self.__menu_id = host.registerCallback(self._gatewaysMenu, with_data=True)
        self.__selected_id = host.registerCallback(
            self._gatewaySelectedCb, with_data=True
        )
        host.importMenu(
            (D_("Service"), D_("Gateways")),
            self._gatewaysMenu,
            security_limit=1,
            help_string=D_("Find gateways"),
        )

    def _gatewaysMenu(self, data, profile):
        """ XMLUI activated by menu: return Gateways UI

        @param profile: %(doc_profile)s
        """
        client = self.host.getClient(profile)
        try:
            jid_ = jid.JID(
                data.get(xml_tools.formEscape("external_jid"), client.jid.host)
            )
        except RuntimeError:
            raise exceptions.DataError(_("Invalid JID"))
        d = self.findGateways(jid_, profile)
        d.addCallback(self._gatewaysResult2XMLUI, jid_)
        d.addCallback(lambda xmlui: {"xmlui": xmlui.toXml()})
        return d

    def _gatewaysResult2XMLUI(self, result, entity):
        xmlui = xml_tools.XMLUI(title=_("Gateways manager (%s)") % entity.full())
        xmlui.addText(_(WARNING_MSG))
        xmlui.addDivider("dash")
        adv_list = xmlui.changeContainer(
            "advanced_list",
            columns=3,
            selectable="single",
            callback_id=self.__selected_id,
        )
        for success, gateway_data in result:
            if not success:
                fail_cond, disco_item = gateway_data
                xmlui.addJid(disco_item.entity)
                xmlui.addText(_("Failed (%s)") % fail_cond)
                xmlui.addEmpty()
            else:
                jid_, data = gateway_data
                for datum in data:
                    identity, name = datum
                    adv_list.setRowIndex(jid_.full())
                    xmlui.addJid(jid_)
                    xmlui.addText(name)
                    xmlui.addText(self._getIdentityDesc(identity))
        adv_list.end()
        xmlui.addDivider("blank")
        xmlui.changeContainer("advanced_list", columns=3)
        xmlui.addLabel(_("Use external XMPP server"))
        xmlui.addString("external_jid")
        xmlui.addButton(self.__menu_id, _(u"Go !"), fields_back=("external_jid",))
        return xmlui

    def _gatewaySelectedCb(self, data, profile):
        try:
            target_jid = jid.JID(data["index"])
        except (KeyError, RuntimeError):
            log.warning(_("No gateway index selected"))
            return {}

        d = self.gatewayRegister(target_jid, profile)
        d.addCallback(lambda xmlui: {"xmlui": xmlui.toXml()})
        return d

    def _getIdentityDesc(self, identity):
        """ Return a human readable description of identity
        @param identity: tuple as returned by Disco identities (category, type)

        """
        category, type_ = identity
        if category != "gateway":
            log.error(
                _(
                    u'INTERNAL ERROR: identity category should always be "gateway" in _getTypeString, got "%s"'
                )
                % category
            )
        try:
            return _(TYPE_DESCRIPTIONS[type_])
        except KeyError:
            return _("Unknown IM")

    def _registrationSuccessful(self, jid_, profile):
        """Called when in_band registration is ok, we must now follow the rest of procedure"""
        log.debug(_("Registration successful, doing the rest"))
        self.host.addContact(jid_, profile_key=profile)
        self.host.setPresence(jid_, profile_key=profile)

    def _gatewayRegister(self, target_jid_s, profile_key=C.PROF_KEY_NONE):
        d = self.gatewayRegister(jid.JID(target_jid_s), profile_key)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def gatewayRegister(self, target_jid, profile_key=C.PROF_KEY_NONE):
        """Register gateway using in-band registration, then log-in to gateway"""
        profile = self.host.memory.getProfileName(profile_key)
        assert profile
        d = self.host.plugins["XEP-0077"].inBandRegister(
            target_jid, self._registrationSuccessful, profile
        )
        return d

    def _infosReceived(self, dl_result, items, target, client):
        """Find disco infos about entity, to check if it is a gateway"""

        ret = []
        for idx, (success, result) in enumerate(dl_result):
            if not success:
                if isinstance(result.value, defer.CancelledError):
                    msg = _("Timeout")
                else:
                    try:
                        msg = result.value.condition
                    except AttributeError:
                        msg = str(result)
                ret.append((success, (msg, items[idx])))
            else:
                entity = items[idx].entity
                gateways = [
                    (identity, result.identities[identity])
                    for identity in result.identities
                    if identity[0] == "gateway"
                ]
                if gateways:
                    log.info(
                        _(u"Found gateway [%(jid)s]: %(identity_name)s")
                        % {
                            "jid": entity.full(),
                            "identity_name": " - ".join(
                                [gateway[1] for gateway in gateways]
                            ),
                        }
                    )
                    ret.append((success, (entity, gateways)))
                else:
                    log.info(
                        _(u"Skipping [%(jid)s] which is not a gateway")
                        % {"jid": entity.full()}
                    )
        return ret

    def _itemsReceived(self, disco, target, client):
        """Look for items with disco protocol, and ask infos for each one"""

        if len(disco._items) == 0:
            log.debug(_("No gateway found"))
            return []

        _defers = []
        for item in disco._items:
            log.debug(_(u"item found: %s") % item.entity)
            _defers.append(client.disco.requestInfo(item.entity))
        dl = defer.DeferredList(_defers)
        dl.addCallback(
            self._infosReceived, items=disco._items, target=target, client=client
        )
        reactor.callLater(GATEWAY_TIMEOUT, dl.cancel)
        return dl

    def _findGateways(self, target_jid_s, profile_key):
        target_jid = jid.JID(target_jid_s)
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            raise exceptions.ProfileUnknownError
        d = self.findGateways(target_jid, profile)
        d.addCallback(self._gatewaysResult2XMLUI, target_jid)
        d.addCallback(lambda xmlui: xmlui.toXml())
        return d

    def findGateways(self, target, profile):
        """Find gateways in the target JID, using discovery protocol
        """
        client = self.host.getClient(profile)
        log.debug(
            _(u"find gateways (target = %(target)s, profile = %(profile)s)")
            % {"target": target.full(), "profile": profile}
        )
        d = client.disco.requestItems(target)
        d.addCallback(self._itemsReceived, target=target, client=client)
        return d

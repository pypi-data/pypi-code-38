#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0115
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
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.internet import defer, error
from zope.interface import implements
from wokkel import disco, iwokkel

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

PRESENCE = "/presence"
NS_ENTITY_CAPABILITY = "http://jabber.org/protocol/caps"
NS_CAPS_OPTIMIZE = "http://jabber.org/protocol/caps#optimize"
CAPABILITY_UPDATE = PRESENCE + '/c[@xmlns="' + NS_ENTITY_CAPABILITY + '"]'

PLUGIN_INFO = {
    C.PI_NAME: "XEP 0115 Plugin",
    C.PI_IMPORT_NAME: "XEP-0115",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0115"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0115",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of entity capabilities"""),
}


class XEP_0115(object):
    cap_hash = None  # capabilities hash is class variable as it is common to all profiles

    def __init__(self, host):
        log.info(_("Plugin XEP_0115 initialization"))
        self.host = host
        host.trigger.add("Presence send", self._presenceTrigger)

    def getHandler(self, client):
        return XEP_0115_handler(self, client.profile)

    @defer.inlineCallbacks
    def _prepareCaps(self, client):
        # we have to calculate hash for client
        # because disco infos/identities may change between clients

        # optimize check
        client._caps_optimize = yield self.host.hasFeature(client, NS_CAPS_OPTIMIZE)
        if client._caps_optimize:
            log.info(_(u"Caps optimisation enabled"))
            client._caps_sent = False
        else:
            log.warning(_(u"Caps optimisation not available"))

        # hash generation
        _infos = yield client.discoHandler.info(client.jid, client.jid, "")
        disco_infos = disco.DiscoInfo()
        for item in _infos:
            disco_infos.append(item)
        cap_hash = client._caps_hash = self.host.memory.disco.generateHash(disco_infos)
        log.info(
            u"Our capability hash has been generated: [{cap_hash}]".format(
                cap_hash=cap_hash
            )
        )
        log.debug(u"Generating capability domish.Element")
        c_elt = domish.Element((NS_ENTITY_CAPABILITY, "c"))
        c_elt["hash"] = "sha-1"
        c_elt["node"] = C.APP_URL
        c_elt["ver"] = cap_hash
        client._caps_elt = c_elt
        if client._caps_optimize:
            client._caps_sent = False
        if cap_hash not in self.host.memory.disco.hashes:
            self.host.memory.disco.hashes[cap_hash] = disco_infos
            self.host.memory.updateEntityData(
                client.jid, C.ENTITY_CAP_HASH, cap_hash, profile_key=client.profile
            )

    def _presenceAddElt(self, client, obj):
        if client._caps_optimize:
            if client._caps_sent:
                return
            client.caps_sent = True
        obj.addChild(client._caps_elt)

    def _presenceTrigger(self, client, obj, presence_d):
        if not hasattr(client, "_caps_optimize"):
            presence_d.addCallback(lambda __: self._prepareCaps(client))

        presence_d.addCallback(lambda __: self._presenceAddElt(client, obj))
        return True


class XEP_0115_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent, profile):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host
        self.profile = profile

    def connectionInitialized(self):
        self.xmlstream.addObserver(CAPABILITY_UPDATE, self.update)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [
            disco.DiscoFeature(NS_ENTITY_CAPABILITY),
            disco.DiscoFeature(NS_CAPS_OPTIMIZE),
        ]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

    def update(self, presence):
        """
        Manage the capabilities of the entity

        Check if we know the version of this capabilities and get the capabilities if necessary
        """
        from_jid = jid.JID(presence["from"])
        c_elem = presence.elements(NS_ENTITY_CAPABILITY, "c").next()
        try:
            c_ver = c_elem["ver"]
            c_hash = c_elem["hash"]
            c_node = c_elem["node"]
        except KeyError:
            log.warning(_(u"Received invalid capabilities tag: %s") % c_elem.toXml())
            return

        if c_ver in self.host.memory.disco.hashes:
            # we already know the hash, we update the jid entity
            log.debug(
                u"hash [%(hash)s] already in cache, updating entity [%(jid)s]"
                % {"hash": c_ver, "jid": from_jid.full()}
            )
            self.host.memory.updateEntityData(
                from_jid, C.ENTITY_CAP_HASH, c_ver, profile_key=self.profile
            )
            return

        if c_hash != "sha-1":  # unknown hash method
            log.warning(
                _(
                    u"Unknown hash method for entity capabilities: [{hash_method}] "
                    u"(entity: {entity_jid}, node: {node})"
                )
                .format(hash_method = c_hash, entity_jid = from_jid, node = c_node)
            )

        def cb(__):
            computed_hash = self.host.memory.getEntityDatum(
                from_jid, C.ENTITY_CAP_HASH, self.profile
            )
            if computed_hash != c_ver:
                log.warning(
                    _(
                        u"Computed hash differ from given hash:\n"
                        u"given: [{given}]\n"
                        u"computed: [{computed}]\n"
                        u"(entity: {entity_jid}, node: {node})"
                    ).format(
                        given = c_ver,
                        computed = computed_hash,
                        entity_jid = from_jid,
                        node = c_node,
                    )
                )

        def eb(failure):
            if isinstance(failure.value, error.ConnectionDone):
                return
            msg = (
                failure.value.condition
                if hasattr(failure.value, "condition")
                else failure.getErrorMessage()
            )
            log.error(
                _(u"Couldn't retrieve disco info for {jid}: {error}").format(
                    jid=from_jid.full(), error=msg
                )
            )

        d = self.host.getDiscoInfos(self.parent, from_jid)
        d.addCallbacks(cb, eb)
        # TODO: me must manage the full algorithm described at XEP-0115 #5.4 part 3

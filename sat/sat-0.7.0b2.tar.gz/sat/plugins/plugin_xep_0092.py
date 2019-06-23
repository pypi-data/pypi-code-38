#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for Software Version (XEP-0092)
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
from twisted.internet import reactor, defer
from twisted.words.protocols.jabber import jid
from wokkel import compat
from sat.core import exceptions
from sat.core.log import getLogger

log = getLogger(__name__)

NS_VERSION = "jabber:iq:version"
TIMEOUT = 10

PLUGIN_INFO = {
    C.PI_NAME: "Software Version Plugin",
    C.PI_IMPORT_NAME: "XEP-0092",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0092"],
    C.PI_DEPENDENCIES: [],
    C.PI_RECOMMENDATIONS: [C.TEXT_CMDS],
    C.PI_MAIN: "XEP_0092",
    C.PI_HANDLER: "no",  # version is already handler in core.xmpp module
    C.PI_DESCRIPTION: _("""Implementation of Software Version"""),
}


class XEP_0092(object):
    def __init__(self, host):
        log.info(_("Plugin XEP_0092 initialization"))
        self.host = host
        host.bridge.addMethod(
            "getSoftwareVersion",
            ".plugin",
            in_sign="ss",
            out_sign="(sss)",
            method=self._getVersion,
            async=True,
        )
        try:
            self.host.plugins[C.TEXT_CMDS].addWhoIsCb(self._whois, 50)
        except KeyError:
            log.info(_("Text commands not available"))

    def _getVersion(self, entity_jid_s, profile_key):
        def prepareForBridge(data):
            name, version, os = data
            return (name or "", version or "", os or "")

        d = self.getVersion(jid.JID(entity_jid_s), profile_key)
        d.addCallback(prepareForBridge)
        return d

    def getVersion(self, jid_, profile_key=C.PROF_KEY_NONE):
        """ Ask version of the client that jid_ is running
        @param jid_: jid from who we want to know client's version
        @param profile_key: %(doc_profile_key)s
        @return (tuple): a defered which fire a tuple with the following data (None if not available):
                 - name: Natural language name of the software
                 - version: specific version of the software
                 - os: operating system of the queried entity
        """
        client = self.host.getClient(profile_key)

        def getVersion(__):
            iq_elt = compat.IQ(client.xmlstream, "get")
            iq_elt["to"] = jid_.full()
            iq_elt.addElement("query", NS_VERSION)
            d = iq_elt.send()
            d.addCallback(self._gotVersion)
            return d

        d = self.host.checkFeature(client, NS_VERSION, jid_)
        d.addCallback(getVersion)
        reactor.callLater(
            TIMEOUT, d.cancel
        )  # XXX: timeout needed because some clients don't answer the IQ
        return d

    def _gotVersion(self, iq_elt):
        try:
            query_elt = iq_elt.elements(NS_VERSION, "query").next()
        except StopIteration:
            raise exceptions.DataError
        ret = []
        for name in ("name", "version", "os"):
            try:
                data_elt = query_elt.elements(NS_VERSION, name).next()
                ret.append(unicode(data_elt))
            except StopIteration:
                ret.append(None)

        return tuple(ret)

    def _whois(self, client, whois_msg, mess_data, target_jid):
        """ Add software/OS information to whois """

        def versionCb(version_data):
            name, version, os = version_data
            if name:
                whois_msg.append(_("Client name: %s") % name)
            if version:
                whois_msg.append(_("Client version: %s") % version)
            if os:
                whois_msg.append(_("Operating system: %s") % os)

        def versionEb(failure):
            failure.trap(exceptions.FeatureNotFound, defer.CancelledError)
            if failure.check(failure, exceptions.FeatureNotFound):
                whois_msg.append(_("Software version not available"))
            else:
                whois_msg.append(_("Client software version request timeout"))

        d = self.getVersion(target_jid, client.profile)
        d.addCallbacks(versionCb, versionEb)
        return d

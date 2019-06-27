#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0095
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
from sat.core import exceptions
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber import error
from zope.interface import implements
from wokkel import disco
from wokkel import iwokkel
import uuid


PLUGIN_INFO = {
    C.PI_NAME: "XEP 0095 Plugin",
    C.PI_IMPORT_NAME: "XEP-0095",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0095"],
    C.PI_MAIN: "XEP_0095",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Stream Initiation"""),
}


IQ_SET = '/iq[@type="set"]'
NS_SI = "http://jabber.org/protocol/si"
SI_REQUEST = IQ_SET + '/si[@xmlns="' + NS_SI + '"]'
SI_PROFILE_HEADER = "http://jabber.org/protocol/si/profile/"
SI_ERROR_CONDITIONS = ("bad-profile", "no-valid-streams")


class XEP_0095(object):
    def __init__(self, host):
        log.info(_("Plugin XEP_0095 initialization"))
        self.host = host
        self.si_profiles = {}  # key: SI profile, value: callback

    def getHandler(self, client):
        return XEP_0095_handler(self)

    def registerSIProfile(self, si_profile, callback):
        """Add a callback for a SI Profile

        @param si_profile(unicode): SI profile name (e.g. file-transfer)
        @param callback(callable): method to call when the profile name is asked
        """
        self.si_profiles[si_profile] = callback

    def unregisterSIProfile(self, si_profile):
        try:
            del self.si_profiles[si_profile]
        except KeyError:
            log.error(
                u"Trying to unregister SI profile [{}] which was not registered".format(
                    si_profile
                )
            )

    def streamInit(self, iq_elt, client):
        """This method is called on stream initiation (XEP-0095 #3.2)

        @param iq_elt: IQ element
        """
        log.info(_("XEP-0095 Stream initiation"))
        iq_elt.handled = True
        si_elt = iq_elt.elements(NS_SI, "si").next()
        si_id = si_elt["id"]
        si_mime_type = iq_elt.getAttribute("mime-type", "application/octet-stream")
        si_profile = si_elt["profile"]
        si_profile_key = (
            si_profile[len(SI_PROFILE_HEADER) :]
            if si_profile.startswith(SI_PROFILE_HEADER)
            else si_profile
        )
        if si_profile_key in self.si_profiles:
            # We know this SI profile, we call the callback
            self.si_profiles[si_profile_key](client, iq_elt, si_id, si_mime_type, si_elt)
        else:
            # We don't know this profile, we send an error
            self.sendError(client, iq_elt, "bad-profile")

    def sendError(self, client, request, condition):
        """Send IQ error as a result

        @param request(domish.Element): original IQ request
        @param condition(str): error condition
        """
        if condition in SI_ERROR_CONDITIONS:
            si_condition = condition
            condition = "bad-request"
        else:
            si_condition = None

        iq_error_elt = error.StanzaError(condition).toResponse(request)
        if si_condition is not None:
            iq_error_elt.error.addElement((NS_SI, si_condition))

        client.send(iq_error_elt)

    def acceptStream(self, client, iq_elt, feature_elt, misc_elts=None):
        """Send the accept stream initiation answer

        @param iq_elt(domish.Element): initial SI request
        @param feature_elt(domish.Element): 'feature' element containing stream method to use
        @param misc_elts(list[domish.Element]): list of elements to add
        """
        log.info(_("sending stream initiation accept answer"))
        if misc_elts is None:
            misc_elts = []
        result_elt = xmlstream.toResponse(iq_elt, "result")
        si_elt = result_elt.addElement((NS_SI, "si"))
        si_elt.addChild(feature_elt)
        for elt in misc_elts:
            si_elt.addChild(elt)
        client.send(result_elt)

    def _parseOfferResult(self, iq_elt):
        try:
            si_elt = iq_elt.elements(NS_SI, "si").next()
        except StopIteration:
            log.warning(u"No <si/> element found in result while expected")
            raise exceptions.DataError
        return (iq_elt, si_elt)

    def proposeStream(
        self,
        client,
        to_jid,
        si_profile,
        feature_elt,
        misc_elts,
        mime_type="application/octet-stream",
    ):
        """Propose a stream initiation

        @param to_jid(jid.JID): recipient
        @param si_profile(unicode): Stream initiation profile (XEP-0095)
        @param feature_elt(domish.Element): feature element, according to XEP-0020
        @param misc_elts(list[domish.Element]): list of elements to add
        @param mime_type(unicode): stream mime type
        @return (tuple): tuple with:
            - session id (unicode)
            - (D(domish_elt, domish_elt): offer deferred which returl a tuple
                with iq_elt and si_elt
        """
        offer = client.IQ()
        sid = str(uuid.uuid4())
        log.debug(_(u"Stream Session ID: %s") % offer["id"])

        offer["from"] = client.jid.full()
        offer["to"] = to_jid.full()
        si = offer.addElement("si", NS_SI)
        si["id"] = sid
        si["mime-type"] = mime_type
        si["profile"] = si_profile
        for elt in misc_elts:
            si.addChild(elt)
        si.addChild(feature_elt)

        offer_d = offer.send()
        offer_d.addCallback(self._parseOfferResult)
        return sid, offer_d


class XEP_0095_handler(xmlstream.XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            SI_REQUEST, self.plugin_parent.streamInit, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_SI)] + [
            disco.DiscoFeature(
                u"http://jabber.org/protocol/si/profile/{}".format(profile_name)
            )
            for profile_name in self.plugin_parent.si_profiles
        ]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Personal Eventing Protocol (xep-0163)
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
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.xish import domish

from wokkel import disco, pubsub
from wokkel.formats import Mood
from sat.tools.common import data_format

NS_USER_MOOD = "http://jabber.org/protocol/mood"

PLUGIN_INFO = {
    C.PI_NAME: "Personal Eventing Protocol Plugin",
    C.PI_IMPORT_NAME: "XEP-0163",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0163", "XEP-0107"],
    C.PI_DEPENDENCIES: ["XEP-0060"],
    C.PI_MAIN: "XEP_0163",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of Personal Eventing Protocol"""),
}


class XEP_0163(object):
    def __init__(self, host):
        log.info(_("PEP plugin initialization"))
        self.host = host
        self.pep_events = set()
        self.pep_out_cb = {}
        host.trigger.add("PubSub Disco Info", self.disoInfoTrigger)
        host.bridge.addMethod(
            "PEPSend",
            ".plugin",
            in_sign="sa{ss}s",
            out_sign="",
            method=self.PEPSend,
            async=True,
        )  # args: type(MOOD, TUNE, etc), data, profile_key;
        self.addPEPEvent("MOOD", NS_USER_MOOD, self.userMoodCB, self.sendMood)

    def disoInfoTrigger(self, disco_info, profile):
        """Add info from managed PEP

        @param disco_info: list of disco feature as returned by PubSub,
            will be filled with PEP features
        @param profile: profile we are handling
        """
        disco_info.extend(map(disco.DiscoFeature, self.pep_events))
        return True

    def addPEPEvent(self, event_type, node, in_callback, out_callback=None, notify=True):
        """Add a Personal Eventing Protocol event manager

        @param event_type(unicode): type of the event (always uppercase),
            can be MOOD, TUNE, etc
        @param node(unicode): namespace of the node (e.g. http://jabber.org/protocol/mood
            for User Mood)
        @param in_callback(callable): method to call when this event occur
            the callable will be called with (itemsEvent, profile) as arguments
        @param out_callback(callable,None): method to call when we want to publish this
            event (must return a deferred)
            the callable will be called when sendPEPEvent is called
        @param notify(bool): add autosubscribe (+notify) if True
        """
        if out_callback:
            self.pep_out_cb[event_type] = out_callback
        self.pep_events.add(node)
        if notify:
            self.pep_events.add(node + "+notify")

        def filterPEPEvent(client, itemsEvent):
            """Ignore messages which are not coming from PEP (i.e. a bare jid)

            @param itemsEvent(pubsub.ItemsEvent): pubsub event
            """
            if not itemsEvent.sender.user or itemsEvent.sender.resource:
                log.debug(
                    "ignoring non PEP event from {} (profile={})".format(
                        itemsEvent.sender.full(), client.profile
                    )
                )
                return
            in_callback(itemsEvent, client.profile)

        self.host.plugins["XEP-0060"].addManagedNode(node, items_cb=filterPEPEvent)

    def sendPEPEvent(self, node, data, profile):
        """Publish the event data

        @param node(unicode): node namespace
        @param data: domish.Element to use as payload
        @param profile: profile which send the data
        """
        client = self.host.getClient(profile)
        item = pubsub.Item(payload=data)
        return self.host.plugins["XEP-0060"].publish(client, None, node, [item])

    def PEPSend(self, event_type, data, profile_key=C.PROF_KEY_NONE):
        """Send personal event after checking the data is alright

        @param event_type: type of event (eg: MOOD, TUNE),
            must be in self.pep_out_cb.keys()
        @param data: dict of {string:string} of event_type dependant data
        @param profile_key: profile who send the event
        """
        profile = self.host.memory.getProfileName(profile_key)
        if not profile:
            log.error(
                _(u"Trying to send personal event with an unknown profile key [%s]")
                % profile_key
            )
            raise exceptions.ProfileUnknownError
        if not event_type in self.pep_out_cb.keys():
            log.error(_("Trying to send personal event for an unknown type"))
            raise exceptions.DataError("Type unknown")
        return self.pep_out_cb[event_type](data, profile)

    def userMoodCB(self, itemsEvent, profile):
        if not itemsEvent.items:
            log.debug(_("No item found"))
            return
        try:
            mood_elt = [
                child for child in itemsEvent.items[0].elements() if child.name == "mood"
            ][0]
        except IndexError:
            log.error(_("Can't find mood element in mood event"))
            return
        mood = Mood.fromXml(mood_elt)
        if not mood:
            log.debug(_("No mood found"))
            return
        self.host.bridge.psEvent(
            C.PS_PEP,
            itemsEvent.sender.full(),
            itemsEvent.nodeIdentifier,
            "MOOD",
            data_format.serialise({"mood": mood.value or "", "text": mood.text or ""}),
            profile,
        )

    def sendMood(self, data, profile):
        """Send XEP-0107's User Mood

        @param data: must include mood and text
        @param profile: profile which send the mood"""
        try:
            value = data["mood"].lower()
            text = data["text"] if "text" in data else ""
        except KeyError:
            raise exceptions.DataError("Mood data must contain at least 'mood' key")
        mood = UserMood(value, text)
        return self.sendPEPEvent(NS_USER_MOOD, mood, profile)


class UserMood(Mood, domish.Element):
    """Improved wokkel Mood which is also a domish.Element"""

    def __init__(self, value, text=None):
        Mood.__init__(self, value, text)
        domish.Element.__init__(self, (NS_USER_MOOD, "mood"))
        self.addElement(value)
        if text:
            self.addElement("text", content=text)

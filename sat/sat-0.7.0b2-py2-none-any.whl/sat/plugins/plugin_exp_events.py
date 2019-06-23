#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin to detect language (experimental)
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

import shortuuid
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.tools import utils
from sat.tools.common import uri as xmpp_uri
from sat.tools.common import date_utils
from twisted.internet import defer
from twisted.words.protocols.jabber import jid, error
from twisted.words.xish import domish
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from wokkel import pubsub

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Events",
    C.PI_IMPORT_NAME: "EVENTS",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [u"XEP-0060", u"INVITATION", u"LIST_INTEREST"],
    C.PI_RECOMMENDATIONS: ["XEP-0277", "EMAIL_INVITATION"],
    C.PI_MAIN: "Events",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(u"""Experimental implementation of XMPP events management"""),
}

NS_EVENT = "org.salut-a-toi.event:0"


class Events(object):
    """Q&D module to handle event attendance answer, experimentation only"""

    def __init__(self, host):
        log.info(_(u"Event plugin initialization"))
        self.host = host
        self._p = self.host.plugins["XEP-0060"]
        self._i = self.host.plugins.get("EMAIL_INVITATION")
        self._b = self.host.plugins.get("XEP-0277")
        self.host.registerNamespace(u"event", NS_EVENT)
        self.host.plugins[u"INVITATION"].registerNamespace(NS_EVENT,
                                                           self.register)
        host.bridge.addMethod(
            "eventGet",
            ".plugin",
            in_sign="ssss",
            out_sign="(ia{ss})",
            method=self._eventGet,
            async=True,
        )
        host.bridge.addMethod(
            "eventCreate",
            ".plugin",
            in_sign="ia{ss}ssss",
            out_sign="s",
            method=self._eventCreate,
            async=True,
        )
        host.bridge.addMethod(
            "eventModify",
            ".plugin",
            in_sign="sssia{ss}s",
            out_sign="",
            method=self._eventModify,
            async=True,
        )
        host.bridge.addMethod(
            "eventsList",
            ".plugin",
            in_sign="sss",
            out_sign="aa{ss}",
            method=self._eventsList,
            async=True,
        )
        host.bridge.addMethod(
            "eventInviteeGet",
            ".plugin",
            in_sign="sss",
            out_sign="a{ss}",
            method=self._eventInviteeGet,
            async=True,
        )
        host.bridge.addMethod(
            "eventInviteeSet",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="",
            method=self._eventInviteeSet,
            async=True,
        )
        host.bridge.addMethod(
            "eventInviteesList",
            ".plugin",
            in_sign="sss",
            out_sign="a{sa{ss}}",
            method=self._eventInviteesList,
            async=True,
        ),
        host.bridge.addMethod(
            "eventInvite",
            ".plugin",
            in_sign="sssss",
            out_sign="",
            method=self._invite,
            async=True,
        )
        host.bridge.addMethod(
            "eventInviteByEmail",
            ".plugin",
            in_sign="ssssassssssss",
            out_sign="",
            method=self._inviteByEmail,
            async=True,
        )

    def getHandler(self, client):
        return EventsHandler(self)

    def _parseEventElt(self, event_elt):
        """Helper method to parse event element

        @param (domish.Element): event_elt
        @return (tuple[int, dict[unicode, unicode]): timestamp, event_data
        """
        try:
            timestamp = date_utils.date_parse(next(event_elt.elements(NS_EVENT, "date")))
        except StopIteration:
            timestamp = -1

        data = {}

        for key in (u"name",):
            try:
                data[key] = event_elt[key]
            except KeyError:
                continue

        for elt_name in (u"description",):
            try:
                elt = next(event_elt.elements(NS_EVENT, elt_name))
            except StopIteration:
                continue
            else:
                data[elt_name] = unicode(elt)

        for elt_name in (u"image", "background-image"):
            try:
                image_elt = next(event_elt.elements(NS_EVENT, elt_name))
                data[elt_name] = image_elt["src"]
            except StopIteration:
                continue
            except KeyError:
                log.warning(_(u"no src found for image"))

        for uri_type in (u"invitees", u"blog"):
            try:
                elt = next(event_elt.elements(NS_EVENT, uri_type))
                uri = data[uri_type + u"_uri"] = elt["uri"]
                uri_data = xmpp_uri.parseXMPPUri(uri)
                if uri_data[u"type"] != u"pubsub":
                    raise ValueError
            except StopIteration:
                log.warning(_(u"no {uri_type} element found!").format(uri_type=uri_type))
            except KeyError:
                log.warning(_(u"incomplete {uri_type} element").format(uri_type=uri_type))
            except ValueError:
                log.warning(_(u"bad {uri_type} element").format(uri_type=uri_type))
            else:
                data[uri_type + u"_service"] = uri_data[u"path"]
                data[uri_type + u"_node"] = uri_data[u"node"]

        for meta_elt in event_elt.elements(NS_EVENT, "meta"):
            key = meta_elt[u"name"]
            if key in data:
                log.warning(
                    u"Ignoring conflicting meta element: {xml}".format(
                        xml=meta_elt.toXml()
                    )
                )
                continue
            data[key] = unicode(meta_elt)
        if event_elt.link:
            link_elt = event_elt.link
            data["service"] = link_elt["service"]
            data["node"] = link_elt["node"]
            data["item"] = link_elt["item"]
        if event_elt.getAttribute("creator") == "true":
            data["creator"] = True
        return timestamp, data

    @defer.inlineCallbacks
    def getEventElement(self, client, service, node, id_):
        """Retrieve event element

        @param service(jid.JID): pubsub service
        @param node(unicode): pubsub node
        @param id_(unicode, None): event id
        @return (domish.Element): event element
        @raise exceptions.NotFound: no event element found
        """
        if not id_:
            id_ = NS_EVENT
        items, metadata = yield self._p.getItems(client, service, node, item_ids=[id_])
        try:
            event_elt = next(items[0].elements(NS_EVENT, u"event"))
        except StopIteration:
            raise exceptions.NotFound(_(u"No event element has been found"))
        except IndexError:
            raise exceptions.NotFound(_(u"No event with this id has been found"))
        defer.returnValue(event_elt)

    def register(self, client, name, extra, service, node, event_id, item_elt,
                 creator=False):
        """Register evenement in personal events list

        @param service(jid.JID): pubsub service of the event
        @param node(unicode): event node
        @param event_id(unicode): event id
        @param event_elt(domish.Element): event element
            note that this element will be modified in place
        @param creator(bool): True if client's profile is the creator of the node
        """
        event_elt = item_elt.event
        link_elt = event_elt.addElement("link")
        link_elt["service"] = service.full()
        link_elt["node"] = node
        link_elt["item"] = event_id
        __, event_data = self._parseEventElt(event_elt)
        name = event_data.get(u'name')
        if u'image' in event_data:
            extra = {u'thumb_url': event_data[u'image']}
        else:
            extra = None
        return self.host.plugins[u'LIST_INTEREST'].registerPubsub(
            client, NS_EVENT, service, node, event_id, creator,
            name=name, element=event_elt, extra=extra)

    def _eventGet(self, service, node, id_=u"", profile_key=C.PROF_KEY_NONE):
        service = jid.JID(service) if service else None
        node = node if node else NS_EVENT
        client = self.host.getClient(profile_key)
        return self.eventGet(client, service, node, id_)

    @defer.inlineCallbacks
    def eventGet(self, client, service, node, id_=NS_EVENT):
        """Retrieve event data

        @param service(unicode, None): PubSub service
        @param node(unicode): PubSub node of the event
        @param id_(unicode): id_ with even data
        @return (tuple[int, dict[unicode, unicode]): event data:
            - timestamp of the event
            - event metadata where key can be:
                location: location of the event
                image: URL of a picture to use to represent event
                background-image: URL of a picture to use in background
        """
        event_elt = yield self.getEventElement(client, service, node, id_)

        defer.returnValue(self._parseEventElt(event_elt))

    def _eventCreate(
        self, timestamp, data, service, node, id_=u"", profile_key=C.PROF_KEY_NONE
    ):
        service = jid.JID(service) if service else None
        node = node or None
        client = self.host.getClient(profile_key)
        data[u"register"] = C.bool(data.get(u"register", C.BOOL_FALSE))
        return self.eventCreate(client, timestamp, data, service, node, id_ or NS_EVENT)

    @defer.inlineCallbacks
    def eventCreate(self, client, timestamp, data, service, node=None, event_id=NS_EVENT):
        """Create or replace an event

        @param service(jid.JID, None): PubSub service
        @param node(unicode, None): PubSub node of the event
            None will create instant node.
        @param event_id(unicode): ID of the item to create.
        @param timestamp(timestamp, None)
        @param data(dict[unicode, unicode]): data to update
            dict will be cleared, do a copy if data are still needed
            key can be:
                - name: name of the event
                - description: details
                - image: main picture of the event
                - background-image: image to use as background
                - register: bool, True if we want to register the event in our local list
        @return (unicode): created node
        """
        if not event_id:
            raise ValueError(_(u"event_id must be set"))
        if not service:
            service = client.jid.userhostJID()
        if not node:
            node = NS_EVENT + u"__" + shortuuid.uuid()
        event_elt = domish.Element((NS_EVENT, "event"))
        if timestamp is not None and timestamp != -1:
            formatted_date = utils.xmpp_date(timestamp)
            event_elt.addElement((NS_EVENT, "date"), content=formatted_date)
        register = data.pop("register", False)
        for key in (u"name",):
            if key in data:
                event_elt[key] = data.pop(key)
        for key in (u"description",):
            if key in data:
                event_elt.addElement((NS_EVENT, key), content=data.pop(key))
        for key in (u"image", u"background-image"):
            if key in data:
                elt = event_elt.addElement((NS_EVENT, key))
                elt["src"] = data.pop(key)

        # we first create the invitees and blog nodes (if not specified in data)
        for uri_type in (u"invitees", u"blog"):
            key = uri_type + u"_uri"
            for to_delete in (u"service", u"node"):
                k = uri_type + u"_" + to_delete
                if k in data:
                    del data[k]
            if key not in data:
                # FIXME: affiliate invitees
                uri_node = yield self._p.createNode(client, service)
                yield self._p.setConfiguration(
                    client,
                    service,
                    uri_node,
                    {self._p.OPT_ACCESS_MODEL: self._p.ACCESS_WHITELIST},
                )
                uri_service = service
            else:
                uri = data.pop(key)
                uri_data = xmpp_uri.parseXMPPUri(uri)
                if uri_data[u"type"] != u"pubsub":
                    raise ValueError(
                        _(u"The given URI is not valid: {uri}").format(uri=uri)
                    )
                uri_service = jid.JID(uri_data[u"path"])
                uri_node = uri_data[u"node"]

            elt = event_elt.addElement((NS_EVENT, uri_type))
            elt["uri"] = xmpp_uri.buildXMPPUri(
                "pubsub", path=uri_service.full(), node=uri_node
            )

        # remaining data are put in <meta> elements
        for key in data.keys():
            elt = event_elt.addElement((NS_EVENT, "meta"), content=data.pop(key))
            elt["name"] = key

        item_elt = pubsub.Item(id=event_id, payload=event_elt)
        try:
            # TODO: check auto-create, no need to create node first if available
            node = yield self._p.createNode(client, service, nodeIdentifier=node)
        except error.StanzaError as e:
            if e.condition == u"conflict":
                log.debug(_(u"requested node already exists"))

        yield self._p.publish(client, service, node, items=[item_elt])

        if register:
            yield self.register(
                client, service, None, {}, node, event_id, event_elt, creator=True)
        defer.returnValue(node)

    def _eventModify(self, service, node, id_, timestamp_update, data_update,
                     profile_key=C.PROF_KEY_NONE):
        service = jid.JID(service) if service else None
        if not node:
            raise ValueError(_(u"missing node"))
        client = self.host.getClient(profile_key)
        return self.eventModify(
            client, service, node, id_ or NS_EVENT, timestamp_update or None, data_update
        )

    @defer.inlineCallbacks
    def eventModify(
        self, client, service, node, id_=NS_EVENT, timestamp_update=None, data_update=None
    ):
        """Update an event

        Similar as create instead that it update existing item instead of
        creating or replacing it. Params are the same as for [eventCreate].
        """
        event_timestamp, event_metadata = yield self.eventGet(client, service, node, id_)
        new_timestamp = event_timestamp if timestamp_update is None else timestamp_update
        new_data = event_metadata
        if data_update:
            for k, v in data_update.iteritems():
                new_data[k] = v
        yield self.eventCreate(client, new_timestamp, new_data, service, node, id_)

    def _eventsListSerialise(self, events):
        for timestamp, data in events:
            data["date"] = unicode(timestamp)
            data["creator"] = C.boolConst(data.get("creator", False))
        return [e[1] for e in events]

    def _eventsList(self, service, node, profile):
        service = jid.JID(service) if service else None
        node = node or None
        client = self.host.getClient(profile)
        d = self.eventsList(client, service, node)
        d.addCallback(self._eventsListSerialise)
        return d

    @defer.inlineCallbacks
    def eventsList(self, client, service, node=None):
        """Retrieve list of registered events

        @return list(tuple(int, dict)): list of events (timestamp + metadata)
        """
        items, metadata = yield self.host.plugins[u'LIST_INTEREST'].listInterests(
            client, service, node, namespace=NS_EVENT)
        events = []
        for item in items:
            try:
                event_elt = next(item.interest.pubsub.elements(NS_EVENT, u"event"))
            except StopIteration:
                log.warning(
                    _(u"No event found in item {item_id}, ignoring").format(
                        item_id=item["id"])
                )
            else:
                timestamp, data = self._parseEventElt(event_elt)
                events.append((timestamp, data))
        defer.returnValue(events)

    def _eventInviteeGet(self, service, node, profile_key):
        service = jid.JID(service) if service else None
        node = node if node else NS_EVENT
        client = self.host.getClient(profile_key)
        return self.eventInviteeGet(client, service, node)

    @defer.inlineCallbacks
    def eventInviteeGet(self, client, service, node):
        """Retrieve attendance from event node

        @param service(unicode, None): PubSub service
        @param node(unicode): PubSub node of the event
        @return (dict): a dict with current attendance status,
            an empty dict is returned if nothing has been answered yed
        """
        try:
            items, metadata = yield self._p.getItems(
                client, service, node, item_ids=[client.jid.userhost()]
            )
            event_elt = next(items[0].elements(NS_EVENT, u"invitee"))
        except (exceptions.NotFound, IndexError):
            # no item found, event data are not set yet
            defer.returnValue({})
        data = {}
        for key in (u"attend", u"guests"):
            try:
                data[key] = event_elt[key]
            except KeyError:
                continue
        defer.returnValue(data)

    def _eventInviteeSet(self, service, node, event_data, profile_key):
        service = jid.JID(service) if service else None
        node = node if node else NS_EVENT
        client = self.host.getClient(profile_key)
        return self.eventInviteeSet(client, service, node, event_data)

    def eventInviteeSet(self, client, service, node, data):
        """Set or update attendance data in event node

        @param service(unicode, None): PubSub service
        @param node(unicode): PubSub node of the event
        @param data(dict[unicode, unicode]): data to update
            key can be:
                attend: one of "yes", "no", "maybe"
                guests: an int
        """
        event_elt = domish.Element((NS_EVENT, "invitee"))
        for key in (u"attend", u"guests"):
            try:
                event_elt[key] = data.pop(key)
            except KeyError:
                pass
        item_elt = pubsub.Item(id=client.jid.userhost(), payload=event_elt)
        return self._p.publish(client, service, node, items=[item_elt])

    def _eventInviteesList(self, service, node, profile_key):
        service = jid.JID(service) if service else None
        node = node if node else NS_EVENT
        client = self.host.getClient(profile_key)
        return self.eventInviteesList(client, service, node)

    @defer.inlineCallbacks
    def eventInviteesList(self, client, service, node):
        """Retrieve attendance from event node

        @param service(unicode, None): PubSub service
        @param node(unicode): PubSub node of the event
        @return (dict): a dict with current attendance status,
            an empty dict is returned if nothing has been answered yed
        """
        items, metadata = yield self._p.getItems(client, service, node)
        invitees = {}
        for item in items:
            try:
                event_elt = next(item.elements(NS_EVENT, u"invitee"))
            except StopIteration:
                # no item found, event data are not set yet
                log.warning(_(
                    u"no data found for {item_id} (service: {service}, node: {node})"
                    .format(item_id=item["id"], service=service, node=node)))
            else:
                data = {}
                for key in (u"attend", u"guests"):
                    try:
                        data[key] = event_elt[key]
                    except KeyError:
                        continue
                invitees[item["id"]] = data
        defer.returnValue(invitees)

    def _invite(self, invitee_jid, service, node, item_id, profile):
        client = self.host.getClient(profile)
        service = jid.JID(service) if service else None
        node = node or None
        item_id = item_id or None
        invitee_jid = jid.JID(invitee_jid)
        return self.invite(client, invitee_jid, service, node, item_id)

    @defer.inlineCallbacks
    def invite(self, client, invitee_jid, service, node, item_id=NS_EVENT):
        """Invite an entity to the event

        This will set permission to let the entity access everything needed
        @pararm invitee_jid(jid.JID): entity to invite
        @param service(jid.JID, None): pubsub service
            None to use client's PEP
        @param node(unicode): event node
        @param item_id(unicode): event id
        """
        # FIXME: handle name and extra
        name = u''
        extra = {}
        if self._b is None:
            raise exceptions.FeatureNotFound(
                _(u'"XEP-0277" (blog) plugin is needed for this feature')
            )
        if item_id is None:
            item_id = NS_EVENT

        # first we authorize our invitee to see the nodes of interest
        yield self._p.setNodeAffiliations(client, service, node, {invitee_jid: u"member"})
        log.debug(_(u"affiliation set on event node"))
        __, event_data = yield self.eventGet(client, service, node, item_id)
        log.debug(_(u"got event data"))
        invitees_service = jid.JID(event_data["invitees_service"])
        invitees_node = event_data["invitees_node"]
        blog_service = jid.JID(event_data["blog_service"])
        blog_node = event_data["blog_node"]
        yield self._p.setNodeAffiliations(
            client, invitees_service, invitees_node, {invitee_jid: u"publisher"}
        )
        log.debug(_(u"affiliation set on invitee node"))
        yield self._p.setNodeAffiliations(
            client, blog_service, blog_node, {invitee_jid: u"member"}
        )
        blog_items, __ = yield self._b.mbGet(client, blog_service, blog_node, None)

        for item in blog_items:
            try:
                comments_service = jid.JID(item["comments_service"])
                comments_node = item["comments_node"]
            except KeyError:
                log.debug(
                    u"no comment service set for item {item_id}".format(
                        item_id=item["id"]
                    )
                )
            else:
                yield self._p.setNodeAffiliations(
                    client, comments_service, comments_node, {invitee_jid: u"publisher"}
                )
        log.debug(_(u"affiliation set on blog and comments nodes"))

        # now we send the invitation
        pubsub_invitation = self.host.plugins[u'INVITATION']
        pubsub_invitation.sendPubsubInvitation(client, invitee_jid, service, node,
                                               item_id, name, extra)

    def _inviteByEmail(self, service, node, id_=NS_EVENT, email=u"", emails_extra=None,
                       name=u"", host_name=u"", language=u"", url_template=u"",
                       message_subject=u"", message_body=u"",
                       profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        kwargs = {
            u"profile": client.profile,
            u"emails_extra": [unicode(e) for e in emails_extra],
        }
        for key in (
            "email",
            "name",
            "host_name",
            "language",
            "url_template",
            "message_subject",
            "message_body",
        ):
            value = locals()[key]
            kwargs[key] = unicode(value)
        return self.inviteByEmail(
            client, jid.JID(service) if service else None, node, id_ or NS_EVENT, **kwargs
        )

    @defer.inlineCallbacks
    def inviteByEmail(self, client, service, node, id_=NS_EVENT, **kwargs):
        """High level method to create an email invitation to an event

        @param service(unicode, None): PubSub service
        @param node(unicode): PubSub node of the event
        @param id_(unicode): id_ with even data
        """
        if self._i is None:
            raise exceptions.FeatureNotFound(
                _(u'"Invitations" plugin is needed for this feature')
            )
        if self._b is None:
            raise exceptions.FeatureNotFound(
                _(u'"XEP-0277" (blog) plugin is needed for this feature')
            )
        service = service or client.jid.userhostJID()
        event_uri = xmpp_uri.buildXMPPUri(
            "pubsub", path=service.full(), node=node, item=id_
        )
        kwargs["extra"] = {u"event_uri": event_uri}
        invitation_data = yield self._i.create(**kwargs)
        invitee_jid = invitation_data[u"jid"]
        log.debug(_(u"invitation created"))
        # now that we have a jid, we can send normal invitation
        yield self.invite(client, invitee_jid, service, node, id_)


class EventsHandler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [
            disco.DiscoFeature(NS_EVENT),
        ]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

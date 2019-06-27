#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Publish-Subscribe (xep-0060)
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
from sat.tools import sat_defer
from sat.tools.common import data_format

from twisted.words.protocols.jabber import jid, error
from twisted.internet import reactor, defer
from wokkel import disco
from wokkel import data_form
from wokkel import generic
from zope.interface import implements
from collections import namedtuple
import urllib

# XXX: sat_tmp.wokkel.pubsub is actually use instead of wokkel version
#      mam and rsm come from sat_tmp.wokkel too
from wokkel import pubsub
from wokkel import rsm
from wokkel import mam


PLUGIN_INFO = {
    C.PI_NAME: u"Publish-Subscribe",
    C.PI_IMPORT_NAME: u"XEP-0060",
    C.PI_TYPE: u"XEP",
    C.PI_PROTOCOLS: [u"XEP-0060"],
    C.PI_DEPENDENCIES: [],
    C.PI_RECOMMENDATIONS: [u"XEP-0059", u"XEP-0313"],
    C.PI_MAIN: u"XEP_0060",
    C.PI_HANDLER: u"yes",
    C.PI_DESCRIPTION: _(u"""Implementation of PubSub Protocol"""),
}

UNSPECIFIED = "unspecified error"


Extra = namedtuple("Extra", ("rsm_request", "extra"))
# rsm_request is the rsm.RSMRequest build with rsm_ prefixed keys, or None
# extra is a potentially empty dict
TIMEOUT = 30

class XEP_0060(object):
    OPT_ACCESS_MODEL = "pubsub#access_model"
    OPT_PERSIST_ITEMS = "pubsub#persist_items"
    OPT_MAX_ITEMS = "pubsub#max_items"
    OPT_DELIVER_PAYLOADS = "pubsub#deliver_payloads"
    OPT_SEND_ITEM_SUBSCRIBE = "pubsub#send_item_subscribe"
    OPT_NODE_TYPE = "pubsub#node_type"
    OPT_SUBSCRIPTION_TYPE = "pubsub#subscription_type"
    OPT_SUBSCRIPTION_DEPTH = "pubsub#subscription_depth"
    OPT_ROSTER_GROUPS_ALLOWED = "pubsub#roster_groups_allowed"
    OPT_PUBLISH_MODEL = "pubsub#publish_model"
    ACCESS_OPEN = "open"
    ACCESS_PRESENCE = "presence"
    ACCESS_ROSTER = "roster"
    ACCESS_PUBLISHER_ROSTER = "publisher-roster"
    ACCESS_AUTHORIZE = "authorize"
    ACCESS_WHITELIST = "whitelist"
    ID_SINGLETON = "current"

    def __init__(self, host):
        log.info(_(u"PubSub plugin initialization"))
        self.host = host
        self._rsm = host.plugins.get(u"XEP-0059")
        self._mam = host.plugins.get(u"XEP-0313")
        self._node_cb = {}  # dictionnary of callbacks for node (key: node, value: list of callbacks)
        self.rt_sessions = sat_defer.RTDeferredSessions()
        host.bridge.addMethod(
            "psNodeCreate",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="s",
            method=self._createNode,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeConfigurationGet",
            ".plugin",
            in_sign="sss",
            out_sign="a{ss}",
            method=self._getNodeConfiguration,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeConfigurationSet",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="",
            method=self._setNodeConfiguration,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeAffiliationsGet",
            ".plugin",
            in_sign="sss",
            out_sign="a{ss}",
            method=self._getNodeAffiliations,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeAffiliationsSet",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="",
            method=self._setNodeAffiliations,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeSubscriptionsGet",
            ".plugin",
            in_sign="sss",
            out_sign="a{ss}",
            method=self._getNodeSubscriptions,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeSubscriptionsSet",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="",
            method=self._setNodeSubscriptions,
            async=True,
        )
        host.bridge.addMethod(
            "psNodePurge",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._purgeNode,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeDelete",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._deleteNode,
            async=True,
        )
        host.bridge.addMethod(
            "psNodeWatchAdd",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._addWatch,
            async=False,
        )
        host.bridge.addMethod(
            "psNodeWatchRemove",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._removeWatch,
            async=False,
        )
        host.bridge.addMethod(
            "psAffiliationsGet",
            ".plugin",
            in_sign="sss",
            out_sign="a{ss}",
            method=self._getAffiliations,
            async=True,
        )
        host.bridge.addMethod(
            "psItemsGet",
            ".plugin",
            in_sign="ssiassa{ss}s",
            out_sign="(asa{ss})",
            method=self._getItems,
            async=True,
        )
        host.bridge.addMethod(
            "psItemSend",
            ".plugin",
            in_sign="ssssa{ss}s",
            out_sign="s",
            method=self._sendItem,
            async=True,
        )
        host.bridge.addMethod(
            "psItemsSend",
            ".plugin",
            in_sign="ssasa{ss}s",
            out_sign="as",
            method=self._sendItems,
            async=True,
        )
        host.bridge.addMethod(
            "psRetractItem",
            ".plugin",
            in_sign="sssbs",
            out_sign="",
            method=self._retractItem,
            async=True,
        )
        host.bridge.addMethod(
            "psRetractItems",
            ".plugin",
            in_sign="ssasbs",
            out_sign="",
            method=self._retractItems,
            async=True,
        )
        host.bridge.addMethod(
            "psSubscribe",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="s",
            method=self._subscribe,
            async=True,
        )
        host.bridge.addMethod(
            "psUnsubscribe",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._unsubscribe,
            async=True,
        )
        host.bridge.addMethod(
            "psSubscriptionsGet",
            ".plugin",
            in_sign="sss",
            out_sign="aa{ss}",
            method=self._subscriptions,
            async=True,
        )
        host.bridge.addMethod(
            "psSubscribeToMany",
            ".plugin",
            in_sign="a(ss)sa{ss}s",
            out_sign="s",
            method=self._subscribeToMany,
        )
        host.bridge.addMethod(
            "psGetSubscribeRTResult",
            ".plugin",
            in_sign="ss",
            out_sign="(ua(sss))",
            method=self._manySubscribeRTResult,
            async=True,
        )
        host.bridge.addMethod(
            "psGetFromMany",
            ".plugin",
            in_sign="a(ss)ia{ss}s",
            out_sign="s",
            method=self._getFromMany,
        )
        host.bridge.addMethod(
            "psGetFromManyRTResult",
            ".plugin",
            in_sign="ss",
            out_sign="(ua(sssasa{ss}))",
            method=self._getFromManyRTResult,
            async=True,
        )

        #  high level observer method
        host.bridge.addSignal(
            "psEvent", ".plugin", signature="ssssss"
        )  # args: category, service(jid), node, type (C.PS_ITEMS, C.PS_DELETE), data, profile

        # low level observer method, used if service/node is in watching list (see psNodeWatch* methods)
        host.bridge.addSignal(
            "psEventRaw", ".plugin", signature="sssass"
        )  # args: service(jid), node, type (C.PS_ITEMS, C.PS_DELETE), list of item_xml, profile

    def getHandler(self, client):
        client.pubsub_client = SatPubSubClient(self.host, self)
        return client.pubsub_client

    @defer.inlineCallbacks
    def profileConnected(self, client):
        client.pubsub_watching = set()
        try:
            client.pubsub_service = jid.JID(
                self.host.memory.getConfig("", "pubsub_service")
            )
        except RuntimeError:
            log.info(
                _(
                    u"Can't retrieve pubsub_service from conf, we'll use first one that we find"
                )
            )
            client.pubsub_service = yield self.host.findServiceEntity(
                client, "pubsub", "service"
            )

    def getFeatures(self, profile):
        try:
            client = self.host.getClient(profile)
        except exceptions.ProfileNotSetError:
            return {}
        try:
            return {
                "service": client.pubsub_service.full()
                if client.pubsub_service is not None
                else ""
            }
        except AttributeError:
            if self.host.isConnected(profile):
                log.debug("Profile is not connected, service is not checked yet")
            else:
                log.error("Service should be available !")
            return {}

    def parseExtra(self, extra):
        """Parse extra dictionnary

        used bridge's extra dictionnaries
        @param extra(dict): extra data used to configure request
        @return(Extra): filled Extra instance
        """
        if extra is None:
            rsm_request = None
            extra = {}
        else:
            # order-by
            if C.KEY_ORDER_BY in extra:
                # FIXME: we temporarily manage only one level of ordering
                #        we need to switch to a fully serialised extra data
                #        to be able to encode a whole ordered list
                extra[C.KEY_ORDER_BY] = [extra.pop(C.KEY_ORDER_BY)]

            # rsm
            if self._rsm is None:
                rsm_request = None
            else:
                rsm_request = self._rsm.parseExtra(extra)

            # mam
            if self._mam is None:
                mam_request = None
            else:
                mam_request = self._mam.parseExtra(extra, with_rsm=False)

            if mam_request is not None:
                assert u"mam" not in extra
                extra[u"mam"] = mam_request

        return Extra(rsm_request, extra)

    def addManagedNode(self, node, **kwargs):
        """Add a handler for a node

        @param node(unicode): node to monitor
            all node *prefixed* with this one will be triggered
        @param **kwargs: method(s) to call when the node is found
            the method must be named after PubSub constants in lower case
            and suffixed with "_cb"
            e.g.: "items_cb" for C.PS_ITEMS, "delete_cb" for C.PS_DELETE
        """
        assert node is not None
        assert kwargs
        callbacks = self._node_cb.setdefault(node, {})
        for event, cb in kwargs.iteritems():
            event_name = event[:-3]
            assert event_name in C.PS_EVENTS
            callbacks.setdefault(event_name, []).append(cb)

    def removeManagedNode(self, node, *args):
        """Add a handler for a node

        @param node(unicode): node to monitor
        @param *args: callback(s) to remove
        """
        assert args
        try:
            registred_cb = self._node_cb[node]
        except KeyError:
            pass
        else:
            for callback in args:
                for event, cb_list in registred_cb.iteritems():
                    try:
                        cb_list.remove(callback)
                    except ValueError:
                        pass
                    else:
                        log.debug(
                            u"removed callback {cb} for event {event} on node {node}".format(
                                cb=callback, event=event, node=node
                            )
                        )
                        if not cb_list:
                            del registred_cb[event]
                        if not registred_cb:
                            del self._node_cb[node]
                        return
        log.error(
            u"Trying to remove inexistant callback {cb} for node {node}".format(
                cb=callback, node=node
            )
        )

    # def listNodes(self, service, nodeIdentifier='', profile=C.PROF_KEY_NONE):
    #     """Retrieve the name of the nodes that are accessible on the target service.

    #     @param service (JID): target service
    #     @param nodeIdentifier (str): the parent node name (leave empty to retrieve first-level nodes)
    #     @param profile (str): %(doc_profile)s
    #     @return: deferred which fire a list of nodes
    #     """
    #     client = self.host.getClient(profile)
    #     d = self.host.getDiscoItems(client, service, nodeIdentifier)
    #     d.addCallback(lambda result: [item.getAttribute('node') for item in result.toElement().children if item.hasAttribute('node')])
    #     return d

    # def listSubscribedNodes(self, service, nodeIdentifier='', filter_='subscribed', profile=C.PROF_KEY_NONE):
    #     """Retrieve the name of the nodes to which the profile is subscribed on the target service.

    #     @param service (JID): target service
    #     @param nodeIdentifier (str): the parent node name (leave empty to retrieve all subscriptions)
    #     @param filter_ (str): filter the result according to the given subscription type:
    #         - None: do not filter
    #         - 'pending': subscription has not been approved yet by the node owner
    #         - 'unconfigured': subscription options have not been configured yet
    #         - 'subscribed': subscription is complete
    #     @param profile (str): %(doc_profile)s
    #     @return: Deferred list[str]
    #     """
    #     d = self.subscriptions(service, nodeIdentifier, profile_key=profile)
    #     d.addCallback(lambda subs: [sub.getAttribute('node') for sub in subs if sub.getAttribute('subscription') == filter_])
    #     return d

    def _sendItem(self, service, nodeIdentifier, payload, item_id=None, extra=None,
                  profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        d = self.sendItem(
            client, service, nodeIdentifier, payload, item_id or None, extra
        )
        d.addCallback(lambda ret: ret or u"")
        return d

    def _sendItems(self, service, nodeIdentifier, items, extra=None,
                  profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        try:
            items = [generic.parseXml(item.encode('utf-8')) for item in items]
        except Exception as e:
            raise exceptions.DataError(_(u"Can't parse items: {msg}").format(
                msg=e))
        d = self.sendItems(
            client, service, nodeIdentifier, items, extra
        )
        return d

    def _getPublishedItemId(self, iq_elt, original_id):
        """return item of published id if found in answer

        if not found original_id is returned, or empty string if it is None or empty
            string
        """
        try:
            item_id = iq_elt.pubsub.publish.item["id"]
        except (AttributeError, KeyError):
            item_id = None
        return item_id or original_id

    def sendItem(self, client, service, nodeIdentifier, payload, item_id=None,
                 extra=None):
        """High level method to send one item

        @param service(jid.JID, None): service to send the item to
            None to use PEP
        @param NodeIdentifier(unicode): PubSub node to use
        @param payload(domish.Element, unicode): payload of the item to send
        @param item_id(unicode, None): id to use or None to create one
        @param extra(dict, None): extra option, not used yet
        @return (unicode, None): id of the created item
        """
        item_elt = pubsub.Item(id=item_id, payload=payload)
        d = self.publish(client, service, nodeIdentifier, [item_elt])
        d.addCallback(self._getPublishedItemId, item_id)
        return d

    def _publishCb(self, iq_result):
        """Parse publish result, and return ids given by pubsub service"""
        try:
            item_ids = [item['id']
                for item in iq_result.pubsub.publish.elements(pubsub.NS_PUBSUB, u'item')]
        except AttributeError:
            return []
        return item_ids

    def sendItems(self, client, service, nodeIdentifier, items, extra=None):
        """High level method to send several items at once

        @param service(jid.JID, None): service to send the item to
            None to use PEP
        @param NodeIdentifier(unicode): PubSub node to use
        @param items(list[domish.Element]): whole item elements to send,
            "id" will be used if set
        @param extra(dict, None): extra option, not used yet
        @return (list[unicode]): ids of the created items
        """
        parsed_items = []
        for item in items:
            if item.name != u'item':
                raise exceptions.DataError(_(u"Invalid item: {xml}").format(item.toXml()))
            item_id = item.getAttribute(u"id")
            parsed_items.append(pubsub.Item(id=item_id, payload=item.firstChildElement()))
        d = self.publish(client, service, nodeIdentifier, parsed_items)
        d.addCallback(self._publishCb)
        return d

    def publish(self, client, service, nodeIdentifier, items=None):
        return client.pubsub_client.publish(
            service, nodeIdentifier, items, client.pubsub_client.parent.jid
        )

    def _unwrapMAMMessage(self, message_elt):
        try:
            item_elt = (
                message_elt.elements(mam.NS_MAM, "result").next()
                .elements(C.NS_FORWARD, "forwarded").next()
                .elements(C.NS_CLIENT, "message").next()
                .elements("http://jabber.org/protocol/pubsub#event", "event").next()
                .elements("http://jabber.org/protocol/pubsub#event", "items").next()
                .elements("http://jabber.org/protocol/pubsub#event", "item").next()
            )
        except StopIteration:
            raise exceptions.DataError(u"Can't find Item in MAM message element")
        return item_elt

    def _getItems(self, service="", node="", max_items=10, item_ids=None, sub_id=None,
                  extra_dict=None, profile_key=C.PROF_KEY_NONE):
        """Get items from pubsub node

        @param max_items(int): maximum number of item to get, C.NO_LIMIT for no limit
        """
        client = self.host.getClient(profile_key)
        service = jid.JID(service) if service else None
        max_items = None if max_items == C.NO_LIMIT else max_items
        extra = self.parseExtra(extra_dict)
        d = self.getItems(
            client,
            service,
            node or None,
            max_items or None,
            item_ids,
            sub_id or None,
            extra.rsm_request,
            extra.extra,
        )
        d.addCallback(self.transItemsData)
        return d

    def getItems(self, client, service, node, max_items=None, item_ids=None, sub_id=None,
                 rsm_request=None, extra=None):
        """Retrieve pubsub items from a node.

        @param service (JID, None): pubsub service.
        @param node (str): node id.
        @param max_items (int): optional limit on the number of retrieved items.
        @param item_ids (list[str]): identifiers of the items to be retrieved (can't be
                                     used with rsm_request).
        @param sub_id (str): optional subscription identifier.
        @param rsm_request (rsm.RSMRequest): RSM request data
        @return: a deferred couple (list[dict], dict) containing:
            - list of items
            - metadata with the following keys:
                - rsm_first, rsm_last, rsm_count, rsm_index: first, last, count and index
                    value of RSMResponse
                - service, node: service and node used
        """
        if item_ids and max_items is not None:
            max_items = None
        if rsm_request and item_ids:
            raise ValueError(u"items_id can't be used with rsm")
        if extra is None:
            extra = {}
        try:
            mam_query = extra["mam"]
        except KeyError:
            d = client.pubsub_client.items(
                service = service,
                nodeIdentifier = node,
                maxItems = max_items,
                subscriptionIdentifier = sub_id,
                sender = None,
                itemIdentifiers = item_ids,
                orderBy = extra.get(C.KEY_ORDER_BY),
                rsm_request = rsm_request
            )
            # we have no MAM data here, so we add None
            d.addCallback(lambda data: data + (None,))
            d.addErrback(sat_defer.stanza2NotFound)
            d.addTimeout(TIMEOUT, reactor)
        else:
            # if mam is requested, we have to do a totally different query
            if self._mam is None:
                raise exceptions.NotFound(u"MAM (XEP-0313) plugin is not available")
            if max_items is not None:
                raise exceptions.DataError(u"max_items parameter can't be used with MAM")
            if item_ids:
                raise exceptions.DataError(u"items_ids parameter can't be used with MAM")
            if mam_query.node is None:
                mam_query.node = node
            elif mam_query.node != node:
                raise exceptions.DataError(
                    u"MAM query node is incoherent with getItems's node"
                )
            if mam_query.rsm is None:
                mam_query.rsm = rsm_request
            else:
                if mam_query.rsm != rsm_request:
                    raise exceptions.DataError(
                        u"Conflict between RSM request and MAM's RSM request"
                    )
            d = self._mam.getArchives(client, mam_query, service, self._unwrapMAMMessage)

        try:
            subscribe = C.bool(extra["subscribe"])
        except KeyError:
            subscribe = False

        def subscribeEb(failure, service, node):
            failure.trap(error.StanzaError)
            log.warning(
                u"Could not subscribe to node {} on service {}: {}".format(
                    node, unicode(service), unicode(failure.value)
                )
            )

        def doSubscribe(data):
            self.subscribe(client, service, node).addErrback(
                subscribeEb, service, node
            )
            return data

        if subscribe:
            d.addCallback(doSubscribe)

        def addMetadata(result):
            # TODO: handle the third argument (mam_response)
            items, rsm_response, mam_response = result
            service_jid = service if service else client.jid.userhostJID()
            metadata = {
                "service": service_jid,
                "node": node,
                "uri": self.getNodeURI(service_jid, node),
            }
            if rsm_request is not None and rsm_response is not None:
                metadata.update(
                    {
                        u"rsm_" + key: value
                        for key, value in rsm_response.toDict().iteritems()
                    }
                )
            if mam_response is not None:
                for key, value in mam_response.iteritems():
                    metadata[u"mam_" + key] = value
            return (items, metadata)

        d.addCallback(addMetadata)
        return d

    # @defer.inlineCallbacks
    # def getItemsFromMany(self, service, data, max_items=None, sub_id=None, rsm=None, profile_key=C.PROF_KEY_NONE):
    #     """Massively retrieve pubsub items from many nodes.
    #     @param service (JID): target service.
    #     @param data (dict): dictionnary binding some arbitrary keys to the node identifiers.
    #     @param max_items (int): optional limit on the number of retrieved items *per node*.
    #     @param sub_id (str): optional subscription identifier.
    #     @param rsm (dict): RSM request data
    #     @param profile_key (str): %(doc_profile_key)s
    #     @return: a deferred dict with:
    #         - key: a value in (a subset of) data.keys()
    #         - couple (list[dict], dict) containing:
    #             - list of items
    #             - RSM response data
    #     """
    #     client = self.host.getClient(profile_key)
    #     found_nodes = yield self.listNodes(service, profile=client.profile)
    #     d_dict = {}
    #     for publisher, node in data.items():
    #         if node not in found_nodes:
    #             log.debug(u"Skip the items retrieval for [{node}]: node doesn't exist".format(node=node))
    #             continue  # avoid pubsub "item-not-found" error
    #         d_dict[publisher] = self.getItems(service, node, max_items, None, sub_id, rsm, client.profile)
    #     defer.returnValue(d_dict)

    def getOptions(self, service, nodeIdentifier, subscriber, subscriptionIdentifier=None,
                   profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        return client.pubsub_client.getOptions(
            service, nodeIdentifier, subscriber, subscriptionIdentifier
        )

    def setOptions(self, service, nodeIdentifier, subscriber, options,
                   subscriptionIdentifier=None, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        return client.pubsub_client.setOptions(
            service, nodeIdentifier, subscriber, options, subscriptionIdentifier
        )

    def _createNode(self, service_s, nodeIdentifier, options, profile_key):
        client = self.host.getClient(profile_key)
        return self.createNode(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier, options
        )

    def createNode(self, client, service, nodeIdentifier=None, options=None):
        """Create a new node

        @param service(jid.JID): PubSub service,
        @param NodeIdentifier(unicode, None): node name
           use None to create instant node (identifier will be returned by this method)
        @param option(dict[unicode, unicode], None): node configuration options
        @return (unicode): identifier of the created node (may be different from requested name)
        """
        # TODO: if pubsub service doesn't hande publish-options, configure it in a second time
        return client.pubsub_client.createNode(service, nodeIdentifier, options)

    @defer.inlineCallbacks
    def createIfNewNode(self, client, service, nodeIdentifier, options=None):
        """Helper method similar to createNode, but will not fail in case of conflict"""
        try:
            yield self.createNode(client, service, nodeIdentifier, options)
        except error.StanzaError as e:
            if e.condition == "conflict":
                pass
            else:
                raise e

    def _getNodeConfiguration(self, service_s, nodeIdentifier, profile_key):
        client = self.host.getClient(profile_key)
        d = self.getConfiguration(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier
        )

        def serialize(form):
            # FIXME: better more generic dataform serialisation should be available in SàT
            return {f.var: unicode(f.value) for f in form.fields.values()}

        d.addCallback(serialize)
        return d

    def getConfiguration(self, client, service, nodeIdentifier):
        request = pubsub.PubSubRequest("configureGet")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier

        def cb(iq):
            form = data_form.findForm(iq.pubsub.configure, pubsub.NS_PUBSUB_NODE_CONFIG)
            form.typeCheck()
            return form

        d = request.send(client.xmlstream)
        d.addCallback(cb)
        return d

    def _setNodeConfiguration(self, service_s, nodeIdentifier, options, profile_key):
        client = self.host.getClient(profile_key)
        d = self.setConfiguration(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier, options
        )
        return d

    def setConfiguration(self, client, service, nodeIdentifier, options):
        request = pubsub.PubSubRequest("configureSet")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier

        form = data_form.Form(
            formType="submit", formNamespace=pubsub.NS_PUBSUB_NODE_CONFIG
        )
        form.makeFields(options)
        request.options = form

        d = request.send(client.xmlstream)
        return d

    def _getAffiliations(self, service_s, nodeIdentifier, profile_key):
        client = self.host.getClient(profile_key)
        d = self.getAffiliations(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier or None
        )
        return d

    def getAffiliations(self, client, service, nodeIdentifier=None):
        """Retrieve affiliations of an entity

        @param nodeIdentifier(unicode, None): node to get affiliation from
            None to get all nodes affiliations for this service
        """
        request = pubsub.PubSubRequest("affiliations")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier

        def cb(iq_elt):
            try:
                affiliations_elt = next(
                    iq_elt.pubsub.elements((pubsub.NS_PUBSUB, "affiliations"))
                )
            except StopIteration:
                raise ValueError(
                    _(u"Invalid result: missing <affiliations> element: {}").format(
                        iq_elt.toXml
                    )
                )
            try:
                return {
                    e["node"]: e["affiliation"]
                    for e in affiliations_elt.elements((pubsub.NS_PUBSUB, "affiliation"))
                }
            except KeyError:
                raise ValueError(
                    _(u"Invalid result: bad <affiliation> element: {}").format(
                        iq_elt.toXml
                    )
                )

        d = request.send(client.xmlstream)
        d.addCallback(cb)
        return d

    def _getNodeAffiliations(self, service_s, nodeIdentifier, profile_key):
        client = self.host.getClient(profile_key)
        d = self.getNodeAffiliations(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier
        )
        d.addCallback(
            lambda affiliations: {j.full(): a for j, a in affiliations.iteritems()}
        )
        return d

    def getNodeAffiliations(self, client, service, nodeIdentifier):
        """Retrieve affiliations of a node owned by profile"""
        request = pubsub.PubSubRequest("affiliationsGet")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier

        def cb(iq_elt):
            try:
                affiliations_elt = next(
                    iq_elt.pubsub.elements((pubsub.NS_PUBSUB_OWNER, "affiliations"))
                )
            except StopIteration:
                raise ValueError(
                    _(u"Invalid result: missing <affiliations> element: {}").format(
                        iq_elt.toXml
                    )
                )
            try:
                return {
                    jid.JID(e["jid"]): e["affiliation"]
                    for e in affiliations_elt.elements(
                        (pubsub.NS_PUBSUB_OWNER, "affiliation")
                    )
                }
            except KeyError:
                raise ValueError(
                    _(u"Invalid result: bad <affiliation> element: {}").format(
                        iq_elt.toXml
                    )
                )

        d = request.send(client.xmlstream)
        d.addCallback(cb)
        return d

    def _setNodeAffiliations(
        self, service_s, nodeIdentifier, affiliations, profile_key=C.PROF_KEY_NONE
    ):
        client = self.host.getClient(profile_key)
        affiliations = {
            jid.JID(jid_): affiliation for jid_, affiliation in affiliations.iteritems()
        }
        d = self.setNodeAffiliations(
            client,
            jid.JID(service_s) if service_s else None,
            nodeIdentifier,
            affiliations,
        )
        return d

    def setNodeAffiliations(self, client, service, nodeIdentifier, affiliations):
        """Update affiliations of a node owned by profile

        @param affiliations(dict[jid.JID, unicode]): affiliations to set
            check https://xmpp.org/extensions/xep-0060.html#affiliations for a list of possible affiliations
        """
        request = pubsub.PubSubRequest("affiliationsSet")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier
        request.affiliations = affiliations
        d = request.send(client.xmlstream)
        return d

    def _purgeNode(self, service_s, nodeIdentifier, profile_key):
        client = self.host.getClient(profile_key)
        return self.purgeNode(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier
        )

    def purgeNode(self, client, service, nodeIdentifier):
        return client.pubsub_client.purgeNode(service, nodeIdentifier)

    def _deleteNode(self, service_s, nodeIdentifier, profile_key):
        client = self.host.getClient(profile_key)
        return self.deleteNode(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier
        )

    def deleteNode(self, client, service, nodeIdentifier):
        return client.pubsub_client.deleteNode(service, nodeIdentifier)

    def _addWatch(self, service_s, node, profile_key):
        """watch modifications on a node

        This method should only be called from bridge
        """
        client = self.host.getClient(profile_key)
        service = jid.JID(service_s) if service_s else client.jid.userhostJID()
        client.pubsub_watching.add((service, node))

    def _removeWatch(self, service_s, node, profile_key):
        """remove a node watch

        This method should only be called from bridge
        """
        client = self.host.getClient(profile_key)
        service = jid.JID(service_s) if service_s else client.jid.userhostJID()
        client.pubsub_watching.remove((service, node))

    def _retractItem(
        self, service_s, nodeIdentifier, itemIdentifier, notify, profile_key
    ):
        return self._retractItems(
            service_s, nodeIdentifier, (itemIdentifier,), notify, profile_key
        )

    def _retractItems(
        self, service_s, nodeIdentifier, itemIdentifiers, notify, profile_key
    ):
        return self.retractItems(
            jid.JID(service_s) if service_s else None,
            nodeIdentifier,
            itemIdentifiers,
            notify,
            profile_key,
        )

    def retractItems(
        self,
        service,
        nodeIdentifier,
        itemIdentifiers,
        notify=True,
        profile_key=C.PROF_KEY_NONE,
    ):
        client = self.host.getClient(profile_key)
        return client.pubsub_client.retractItems(
            service, nodeIdentifier, itemIdentifiers, notify=True
        )

    def _subscribe(self, service, nodeIdentifier, options, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        d = self.subscribe(client, service, nodeIdentifier, options=options or None)
        d.addCallback(lambda subscription: subscription.subscriptionIdentifier or u"")
        return d

    def subscribe(self, client, service, nodeIdentifier, sub_jid=None, options=None):
        # TODO: reimplement a subscribtion cache, checking that we have not subscription before trying to subscribe
        return client.pubsub_client.subscribe(
            service, nodeIdentifier, sub_jid or client.jid.userhostJID(), options=options
        )

    def _unsubscribe(self, service, nodeIdentifier, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        return self.unsubscribe(client, service, nodeIdentifier)

    def unsubscribe(
        self,
        client,
        service,
        nodeIdentifier,
        sub_jid=None,
        subscriptionIdentifier=None,
        sender=None,
    ):
        return client.pubsub_client.unsubscribe(
            service,
            nodeIdentifier,
            sub_jid or client.jid.userhostJID(),
            subscriptionIdentifier,
            sender,
        )

    def _subscriptions(self, service, nodeIdentifier="", profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)

        def gotSubscriptions(subscriptions):
            # we replace pubsub.Subscription instance by dict that we can serialize
            for idx, sub in enumerate(subscriptions):
                sub_dict = {
                    "node": sub.nodeIdentifier,
                    "subscriber": sub.subscriber.full(),
                    "state": sub.state,
                }
                if sub.subscriptionIdentifier is not None:
                    sub_dict["id"] = sub.subscriptionIdentifier
                subscriptions[idx] = sub_dict

            return subscriptions

        d = self.subscriptions(client, service, nodeIdentifier or None)
        d.addCallback(gotSubscriptions)
        return d

    def subscriptions(self, client, service, nodeIdentifier=None):
        """retrieve subscriptions from a service

        @param service(jid.JID): PubSub service
        @param nodeIdentifier(unicode, None): node to check
            None to get all subscriptions
        """
        return client.pubsub_client.subscriptions(service, nodeIdentifier)

    ## misc tools ##

    def getNodeURI(self, service, node, item=None):
        """Return XMPP URI of a PubSub node

        @param service(jid.JID): PubSub service
        @param node(unicode): node
        @return (unicode): URI of the node
        """
        assert service is not None
        # XXX: urllib.urlencode use "&" to separate value, while XMPP URL (cf. RFC 5122)
        #      use ";" as a separator. So if more than one value is used in query_data,
        #      urlencode MUST NOT BE USED.
        query_data = [("node", node.encode("utf-8"))]
        if item is not None:
            query_data.append(("item", item.encode("utf-8")))
        return "xmpp:{service}?;{query}".format(
            service=service.userhost(), query=urllib.urlencode(query_data)
        ).decode("utf-8")

    ## methods to manage several stanzas/jids at once ##

    # generic #

    def getRTResults(
        self, session_id, on_success=None, on_error=None, profile=C.PROF_KEY_NONE
    ):
        return self.rt_sessions.getResults(session_id, on_success, on_error, profile)

    def transItemsData(self, items_data, item_cb=lambda item: item.toXml(),
            serialise=False):
        """Helper method to transform result from [getItems]

        the items_data must be a tuple(list[domish.Element], dict[unicode, unicode])
        as returned by [getItems]. metadata values are then casted to unicode and
        each item is passed to items_cb then optionally serialised with
            data_format.serialise.
        @param items_data(tuple): tuple returned by [getItems]
        @param item_cb(callable): method to transform each item
        @param serialise(bool): if True do a data_format.serialise
            after applying item_cb
        @return (tuple): a serialised form ready to go throught bridge
        """
        items, metadata = items_data
        if serialise:
            items = [data_format.serialise(item_cb(item)) for item in items]
        else:
            items = [item_cb(item) for item in items]

        return (
            items,
            {key: unicode(value) for key, value in metadata.iteritems()},
        )

    def transItemsDataD(self, items_data, item_cb, serialise=False):
        """Helper method to transform result from [getItems], deferred version

        the items_data must be a tuple(list[domish.Element], dict[unicode, unicode])
        as returned by [getItems]. metadata values are then casted to unicode and
        each item is passed to items_cb then optionally serialised with
            data_format.serialise.
        An errback is added to item_cb, and when it is fired the value is filtered from
            final items
        @param items_data(tuple): tuple returned by [getItems]
        @param item_cb(callable): method to transform each item (must return a deferred)
        @param serialise(bool): if True do a data_format.serialise
            after applying item_cb
        @return (tuple): a deferred which fire a serialised form ready to go throught
            bridge
        """
        items, metadata = items_data

        def eb(failure):
            log.warning(
                "Error while serialising/parsing item: {}".format(unicode(failure.value))
            )

        d = defer.gatherResults([item_cb(item).addErrback(eb) for item in items])

        def finishSerialisation(parsed_items):
            if serialise:
                items = [data_format.serialise(i) for i in parsed_items if i is not None]
            else:
                items = [i for i in parsed_items if i is not None]

            return (
                items,
                {key: unicode(value) for key, value in metadata.iteritems()},
            )

        d.addCallback(finishSerialisation)
        return d

    def serDList(self, results, failure_result=None):
        """Serialise a DeferredList result

        @param results: DeferredList results
        @param failure_result: value to use as value for failed Deferred
            (default: empty tuple)
        @return (list): list with:
            - failure: empty in case of success, else error message
            - result
        """
        if failure_result is None:
            failure_result = ()
        return [
            ("", result)
            if success
            else (unicode(result.result) or UNSPECIFIED, failure_result)
            for success, result in results
        ]

    # subscribe #

    def _getNodeSubscriptions(self, service_s, nodeIdentifier, profile_key):
        client = self.host.getClient(profile_key)
        d = self.getNodeSubscriptions(
            client, jid.JID(service_s) if service_s else None, nodeIdentifier
        )
        d.addCallback(
            lambda subscriptions: {j.full(): a for j, a in subscriptions.iteritems()}
        )
        return d

    def getNodeSubscriptions(self, client, service, nodeIdentifier):
        """Retrieve subscriptions to a node

        @param nodeIdentifier(unicode): node to get subscriptions from
        """
        if not nodeIdentifier:
            raise exceptions.DataError("node identifier can't be empty")
        request = pubsub.PubSubRequest("subscriptionsGet")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier

        def cb(iq_elt):
            try:
                subscriptions_elt = next(
                    iq_elt.pubsub.elements((pubsub.NS_PUBSUB, "subscriptions"))
                )
            except StopIteration:
                raise ValueError(
                    _(u"Invalid result: missing <subscriptions> element: {}").format(
                        iq_elt.toXml
                    )
                )
            except AttributeError as e:
                raise ValueError(_(u"Invalid result: {}").format(e))
            try:
                return {
                    jid.JID(s["jid"]): s["subscription"]
                    for s in subscriptions_elt.elements(
                        (pubsub.NS_PUBSUB, "subscription")
                    )
                }
            except KeyError:
                raise ValueError(
                    _(u"Invalid result: bad <subscription> element: {}").format(
                        iq_elt.toXml
                    )
                )

        d = request.send(client.xmlstream)
        d.addCallback(cb)
        return d

    def _setNodeSubscriptions(
        self, service_s, nodeIdentifier, subscriptions, profile_key=C.PROF_KEY_NONE
    ):
        client = self.host.getClient(profile_key)
        subscriptions = {
            jid.JID(jid_): subscription
            for jid_, subscription in subscriptions.iteritems()
        }
        d = self.setNodeSubscriptions(
            client,
            jid.JID(service_s) if service_s else None,
            nodeIdentifier,
            subscriptions,
        )
        return d

    def setNodeSubscriptions(self, client, service, nodeIdentifier, subscriptions):
        """Set or update subscriptions of a node owned by profile

        @param subscriptions(dict[jid.JID, unicode]): subscriptions to set
            check https://xmpp.org/extensions/xep-0060.html#substates for a list of possible subscriptions
        """
        request = pubsub.PubSubRequest("subscriptionsSet")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier
        request.subscriptions = {
            pubsub.Subscription(nodeIdentifier, jid_, state)
            for jid_, state in subscriptions.iteritems()
        }
        d = request.send(client.xmlstream)
        return d

    def _manySubscribeRTResult(self, session_id, profile_key=C.PROF_KEY_DEFAULT):
        """Get real-time results for subcribeToManu session

        @param session_id: id of the real-time deferred session
        @param return (tuple): (remaining, results) where:
            - remaining is the number of still expected results
            - results is a list of tuple(unicode, unicode, bool, unicode) with:
                - service: pubsub service
                - and node: pubsub node
                - failure(unicode): empty string in case of success, error message else
        @param profile_key: %(doc_profile_key)s
        """
        profile = self.host.getClient(profile_key).profile
        d = self.rt_sessions.getResults(
            session_id,
            on_success=lambda result: "",
            on_error=lambda failure: unicode(failure.value),
            profile=profile,
        )
        # we need to convert jid.JID to unicode with full() to serialise it for the bridge
        d.addCallback(
            lambda ret: (
                ret[0],
                [
                    (service.full(), node, "" if success else failure or UNSPECIFIED)
                    for (service, node), (success, failure) in ret[1].iteritems()
                ],
            )
        )
        return d

    def _subscribeToMany(
        self, node_data, subscriber=None, options=None, profile_key=C.PROF_KEY_NONE
    ):
        return self.subscribeToMany(
            [(jid.JID(service), unicode(node)) for service, node in node_data],
            jid.JID(subscriber),
            options,
            profile_key,
        )

    def subscribeToMany(
        self, node_data, subscriber, options=None, profile_key=C.PROF_KEY_NONE
    ):
        """Subscribe to several nodes at once.

        @param node_data (iterable[tuple]): iterable of tuple (service, node) where:
            - service (jid.JID) is the pubsub service
            - node (unicode) is the node to subscribe to
        @param subscriber (jid.JID): optional subscription identifier.
        @param options (dict): subscription options
        @param profile_key (str): %(doc_profile_key)s
        @return (str): RT Deferred session id
        """
        client = self.host.getClient(profile_key)
        deferreds = {}
        for service, node in node_data:
            deferreds[(service, node)] = client.pubsub_client.subscribe(
                service, node, subscriber, options=options
            )
        return self.rt_sessions.newSession(deferreds, client.profile)
        # found_nodes = yield self.listNodes(service, profile=client.profile)
        # subscribed_nodes = yield self.listSubscribedNodes(service, profile=client.profile)
        # d_list = []
        # for nodeIdentifier in (set(nodeIdentifiers) - set(subscribed_nodes)):
        #     if nodeIdentifier not in found_nodes:
        #         log.debug(u"Skip the subscription to [{node}]: node doesn't exist".format(node=nodeIdentifier))
        #         continue  # avoid sat-pubsub "SubscriptionExists" error
        #     d_list.append(client.pubsub_client.subscribe(service, nodeIdentifier, sub_jid or client.pubsub_client.parent.jid.userhostJID(), options=options))
        # defer.returnValue(d_list)

    # get #

    def _getFromManyRTResult(self, session_id, profile_key=C.PROF_KEY_DEFAULT):
        """Get real-time results for getFromMany session

        @param session_id: id of the real-time deferred session
        @param profile_key: %(doc_profile_key)s
        @param return (tuple): (remaining, results) where:
            - remaining is the number of still expected results
            - results is a list of tuple with
                - service (unicode): pubsub service
                - node (unicode): pubsub node
                - failure (unicode): empty string in case of success, error message else
                - items (list[s]): raw XML of items
                - metadata(dict): serialised metadata
        """
        profile = self.host.getClient(profile_key).profile
        d = self.rt_sessions.getResults(
            session_id,
            on_success=lambda result: ("", self.transItemsData(result)),
            on_error=lambda failure: (unicode(failure.value) or UNSPECIFIED, ([], {})),
            profile=profile,
        )
        d.addCallback(
            lambda ret: (
                ret[0],
                [
                    (service.full(), node, failure, items, metadata)
                    for (service, node), (success, (failure, (items, metadata))) in ret[
                        1
                    ].iteritems()
                ],
            )
        )
        return d

    def _getFromMany(
        self, node_data, max_item=10, extra_dict=None, profile_key=C.PROF_KEY_NONE
    ):
        """
        @param max_item(int): maximum number of item to get, C.NO_LIMIT for no limit
        """
        max_item = None if max_item == C.NO_LIMIT else max_item
        extra = self.parseExtra(extra_dict)
        return self.getFromMany(
            [(jid.JID(service), unicode(node)) for service, node in node_data],
            max_item,
            extra.rsm_request,
            extra.extra,
            profile_key,
        )

    def getFromMany(self, node_data, max_item=None, rsm_request=None, extra=None,
                    profile_key=C.PROF_KEY_NONE):
        """Get items from many nodes at once

        @param node_data (iterable[tuple]): iterable of tuple (service, node) where:
            - service (jid.JID) is the pubsub service
            - node (unicode) is the node to get items from
        @param max_items (int): optional limit on the number of retrieved items.
        @param rsm_request (RSMRequest): RSM request data
        @param profile_key (unicode): %(doc_profile_key)s
        @return (str): RT Deferred session id
        """
        client = self.host.getClient(profile_key)
        deferreds = {}
        for service, node in node_data:
            deferreds[(service, node)] = self.getItems(
                client, service, node, max_item, rsm_request=rsm_request, extra=extra
            )
        return self.rt_sessions.newSession(deferreds, client.profile)


class SatPubSubClient(rsm.PubSubClient):
    implements(disco.IDisco)

    def __init__(self, host, parent_plugin):
        self.host = host
        self.parent_plugin = parent_plugin
        rsm.PubSubClient.__init__(self)

    def connectionInitialized(self):
        rsm.PubSubClient.connectionInitialized(self)

    def _getNodeCallbacks(self, node, event):
        """Generate callbacks from given node and event

        @param node(unicode): node used for the item
            any registered node which prefix the node will match
        @param event(unicode): one of C.PS_ITEMS, C.PS_RETRACT, C.PS_DELETE
        @return (iterator[callable]): callbacks for this node/event
        """
        for registered_node, callbacks_dict in self.parent_plugin._node_cb.iteritems():
            if not node.startswith(registered_node):
                continue
            try:
                for callback in callbacks_dict[event]:
                    yield callback
            except KeyError:
                continue


    def itemsReceived(self, event):
        log.debug(u"Pubsub items received")
        for callback in self._getNodeCallbacks(event.nodeIdentifier, C.PS_ITEMS):
            callback(self.parent, event)
        client = self.parent
        if (event.sender, event.nodeIdentifier) in client.pubsub_watching:
            raw_items = [i.toXml() for i in event.items]
            self.host.bridge.psEventRaw(
                event.sender.full(),
                event.nodeIdentifier,
                C.PS_ITEMS,
                raw_items,
                client.profile,
            )

    def deleteReceived(self, event):
        log.debug((u"Publish node deleted"))
        for callback in self._getNodeCallbacks(event.nodeIdentifier, C.PS_DELETE):
            callback(self.parent, event)
        client = self.parent
        if (event.sender, event.nodeIdentifier) in client.pubsub_watching:
            self.host.bridge.psEventRaw(
                event.sender.full(), event.nodeIdentifier, C.PS_DELETE, [], client.profile
            )

    def subscriptions(self, service, nodeIdentifier, sender=None):
        """Return the list of subscriptions to the given service and node.

        @param service: The publish subscribe service to retrieve the subscriptions from.
        @type service: L{JID<twisted.words.protocols.jabber.jid.JID>}
        @param nodeIdentifier: The identifier of the node (leave empty to retrieve all subscriptions).
        @type nodeIdentifier: C{unicode}
        @return (list[pubsub.Subscription]): list of subscriptions
        """
        request = pubsub.PubSubRequest("subscriptions")
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier
        request.sender = sender
        d = request.send(self.xmlstream)

        def cb(iq):
            subs = []
            for subscription_elt in iq.pubsub.subscriptions.elements(
                pubsub.NS_PUBSUB, "subscription"
            ):
                subscription = pubsub.Subscription(
                    subscription_elt["node"],
                    jid.JID(subscription_elt["jid"]),
                    subscription_elt["subscription"],
                    subscriptionIdentifier=subscription_elt.getAttribute("subid"),
                )
                subs.append(subscription)
            return subs

        return d.addCallback(cb)

    def purgeNode(self, service, nodeIdentifier):
        """Purge a node (i.e. delete all items from it)

        @param service(jid.JID, None): service to send the item to
            None to use PEP
        @param NodeIdentifier(unicode): PubSub node to use
        """
        # TODO: propose this upstream and remove it once merged
        request = pubsub.PubSubRequest('purge')
        request.recipient = service
        request.nodeIdentifier = nodeIdentifier
        return request.send(self.xmlstream)

    def getDiscoInfo(self, requestor, service, nodeIdentifier=""):
        disco_info = []
        self.host.trigger.point("PubSub Disco Info", disco_info, self.parent.profile)
        return disco_info

    def getDiscoItems(self, requestor, service, nodeIdentifier=""):
        return []

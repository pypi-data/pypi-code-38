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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger
from wokkel import disco, iwokkel, pubsub
from zope.interface import implements
from twisted.internet import defer
from twisted.words.protocols.jabber import error as jabber_error, jid
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.words.xish import domish

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "List of Interest",
    C.PI_IMPORT_NAME: "LIST_INTEREST",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [u"XEP-0060", u"XEP-0329"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "ListInterest",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(u"Experimental handling of interesting XMPP locations"),
}

NS_LIST_INTEREST = "https://salut-a-toi/protocol/list-interest:0"


class ListInterest(object):
    namespace = NS_LIST_INTEREST

    def __init__(self, host):
        log.info(_(u"List of Interest plugin initialization"))
        self.host = host
        self._p = self.host.plugins["XEP-0060"]
        host.bridge.addMethod(
            "interestsList",
            ".plugin",
            in_sign="ssss",
            out_sign="aa{ss}",
            method=self._listInterests,
            async=True,
        )

    def getHandler(self, client):
        return ListInterestHandler(self)

    @defer.inlineCallbacks
    def createNode(self, client):
        try:
            # TODO: check auto-create, no need to create node first if available
            options = {self._p.OPT_ACCESS_MODEL: self._p.ACCESS_WHITELIST}
            yield self._p.createNode(
                client,
                client.jid.userhostJID(),
                nodeIdentifier=NS_LIST_INTEREST,
                options=options,
            )
        except jabber_error.StanzaError as e:
            if e.condition == u"conflict":
                log.debug(_(u"requested node already exists"))

    @defer.inlineCallbacks
    def registerPubsub(self, client, namespace, service, node, item_id=None,
                       creator=False, name=None, element=None, extra=None):
        """Register an interesting element in personal list

        @param namespace(unicode): namespace of the interest
            this is used as a cache, to avoid the need to retrieve the item only to get
            its namespace
        @param service(jid.JID): target pubsub service
        @param node(unicode): target pubsub node
        @param item_id(unicode, None): target pubsub id
        @param creator(bool): True if client's profile is the creator of the node
            This is used a cache, to avoid the need to retrieve affiliations
        @param name(unicode, None): name of the interest
        @param element(domish.Element, None): element to attach
            may be used to cache some extra data
        @param extra(dict, None): extra data, key can be:
            - thumb_url: http(s) URL of a thumbnail
        """
        if extra is None:
            extra = {}
        yield self.createNode(client)
        interest_elt = domish.Element((NS_LIST_INTEREST, u"interest"))
        interest_elt[u"namespace"] = namespace
        if name is not None:
            interest_elt[u'name'] = name
        thumb_url = extra.get(u'thumb_url')
        if thumb_url:
            interest_elt[u'thumb_url'] = thumb_url
        pubsub_elt = interest_elt.addElement(u"pubsub")
        pubsub_elt[u"service"] = service.full()
        pubsub_elt[u"node"] = node
        if item_id is not None:
            pubsub_elt[u"item"] = item_id
        if creator:
            pubsub_elt[u"creator"] = C.BOOL_TRUE
        if element is not None:
            pubsub_elt.addChild(element)
        item_elt = pubsub.Item(payload=interest_elt)
        yield self._p.publish(
            client, client.jid.userhostJID(), NS_LIST_INTEREST, items=[item_elt]
        )

    @defer.inlineCallbacks
    def registerFileSharing(
            self, client, service, repos_type=None, namespace=None, path=None, name=None,
            extra=None):
        """Register an interesting file repository in personal list

        @param service(jid.JID): service of the file repository
        @param repos_type(unicode): type of the repository
        @param namespace(unicode, None): namespace of the repository
        @param path(unicode, None): path of the repository
        @param name(unicode, None): name of the repository
        @param extra(dict, None): as ad for [registerPubsub]
        """
        if extra is None:
            extra = {}
        yield self.createNode(client)
        interest_elt = domish.Element((NS_LIST_INTEREST, u"interest"))
        interest_elt[u"namespace"] = self.host.getNamespace(u"fis")
        if name is not None:
            interest_elt[u'name'] = name
        thumb_url = extra.get(u'thumb_url')
        if thumb_url:
            interest_elt[u'thumb_url'] = thumb_url
        file_sharing_elt = interest_elt.addElement(u"file_sharing")
        file_sharing_elt[u"service"] = service.full()
        if repos_type is not None:
            file_sharing_elt[u"type"] = repos_type
        if namespace is not None:
            file_sharing_elt[u"namespace"] = namespace
        if path is not None:
            file_sharing_elt[u"path"] = path
        item_elt = pubsub.Item(payload=interest_elt)
        yield self._p.publish(
            client, client.jid.userhostJID(), NS_LIST_INTEREST, items=[item_elt]
        )

    def _listInterestsSerialise(self, interests_data):
        interests = []
        for item_elt in interests_data[0]:
            interest_data = {}
            interest_elt = item_elt.interest
            if interest_elt.hasAttribute(u'namespace'):
                interest_data[u'namespace'] = interest_elt.getAttribute(u'namespace')
            if interest_elt.hasAttribute(u'name'):
                interest_data[u'name'] = interest_elt.getAttribute(u'name')
            if interest_elt.hasAttribute(u'thumb_url'):
                interest_data[u'thumb_url'] = interest_elt.getAttribute(u'thumb_url')
            elt = interest_elt.firstChildElement()
            if elt.uri != NS_LIST_INTEREST:
                log.warning(u"unexpected child element, ignoring: {xml}".format(
                    xml = elt.toXml()))
                continue
            if elt.name == u'pubsub':
                interest_data.update({
                    u"type": u"pubsub",
                    u"service": elt[u'service'],
                    u"node": elt[u'node'],
                })
                for attr in (u'item', u'creator'):
                    if elt.hasAttribute(attr):
                        interest_data[attr] = elt[attr]
            elif elt.name == u'file_sharing':
                interest_data.update({
                    u"type": u"file_sharing",
                    u"service": elt[u'service'],
                })
                if elt.hasAttribute(u'type'):
                    interest_data[u'subtype'] = elt[u'type']
                for attr in (u'namespace', u'path'):
                    if elt.hasAttribute(attr):
                        interest_data[attr] = elt[attr]
            else:
                log.warning(u"unknown element, ignoring: {xml}".format(xml=elt.toXml()))
                continue
            interests.append(interest_data)

        return interests

    def _listInterests(self, service, node, namespace, profile):
        service = jid.JID(service) if service else None
        node = node or None
        namespace = namespace or None
        client = self.host.getClient(profile)
        d = self.listInterests(client, service, node, namespace)
        d.addCallback(self._listInterestsSerialise)
        return d

    @defer.inlineCallbacks
    def listInterests(self, client, service=None, node=None, namespace=None):
        """Retrieve list of interests

        @param service(jid.JID, None): service to use
            None to use own PEP
        @param node(unicode, None): node to use
            None to use default node
        @param namespace(unicode, None): filter interests of this namespace
            None to retrieve all interests
        @return: same as [XEP_0060.getItems]
        """
        # TODO: if a MAM filter were available, it would improve performances
        if not node:
            node = NS_LIST_INTEREST
        items, metadata = yield self._p.getItems(client, service, node)
        if namespace is not None:
            filtered_items = []
            for item in items:
                try:
                    interest_elt = next(item.elements(NS_LIST_INTEREST, u"interest"))
                except StopIteration:
                    log.warning(_(u"Missing interest element: {xml}").format(
                        xml=interest_elt.toXml()))
                    continue
                if interest_elt.getAttribute(u"namespace") == namespace:
                    filtered_items.append(item)
            items = filtered_items

        defer.returnValue((items, metadata))


class ListInterestHandler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [
            disco.DiscoFeature(NS_LIST_INTEREST),
        ]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

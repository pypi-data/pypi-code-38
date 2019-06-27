#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.error import StanzaError
from twisted.internet import defer
from twisted.internet import reactor
from twisted.python import failure
from sat.core.constants import Const as C
from sat.tools import xml_tools
from sat.memory import persistent
from wokkel import disco
from base64 import b64encode
from hashlib import sha1


TIMEOUT = 15
CAP_HASH_ERROR = "ERROR"


class HashGenerationError(Exception):
    pass


class ByteIdentity(object):
    """This class manage identity as bytes (needed for i;octet sort), it is used for the hash generation"""

    def __init__(self, identity, lang=None):
        assert isinstance(identity, disco.DiscoIdentity)
        self.category = identity.category.encode("utf-8")
        self.idType = identity.type.encode("utf-8")
        self.name = identity.name.encode("utf-8") if identity.name else ""
        self.lang = lang.encode("utf-8") if lang is not None else ""

    def __str__(self):
        return "%s/%s/%s/%s" % (self.category, self.idType, self.lang, self.name)


class HashManager(object):
    """map object which manage hashes

    persistent storage is update when a new hash is added
    """

    def __init__(self, persistent):
        self.hashes = {
            CAP_HASH_ERROR: disco.DiscoInfo()  # used when we can't get disco infos
        }
        self.persistent = persistent

    def __getitem__(self, key):
        return self.hashes[key]

    def __setitem__(self, hash_, disco_info):
        if hash_ in self.hashes:
            log.debug(u"ignoring hash set: it is already known")
            return
        self.hashes[hash_] = disco_info
        self.persistent[hash_] = disco_info.toElement().toXml()

    def __contains__(self, hash_):
        return self.hashes.__contains__(hash_)

    def load(self):
        def fillHashes(hashes):
            for hash_, xml in hashes.iteritems():
                element = xml_tools.ElementParser()(xml)
                disco_info = disco.DiscoInfo.fromElement(element)
                if not disco_info.features and not disco_info.identities:
                    log.warning(
                        _(
                            u"no feature/identity found in disco element (hash: {cap_hash}), ignoring: {xml}"
                        ).format(cap_hash=hash_, xml=xml)
                    )
                else:
                    self.hashes[hash_] = disco_info

            log.info(u"Disco hashes loaded")

        d = self.persistent.load()
        d.addCallback(fillHashes)
        return d


class Discovery(object):
    """ Manage capabilities of entities """

    def __init__(self, host):
        self.host = host
        # TODO: remove legacy hashes

    def load(self):
        """Load persistent hashes"""
        self.hashes = HashManager(persistent.PersistentDict("disco"))
        return self.hashes.load()

    @defer.inlineCallbacks
    def hasFeature(self, client, feature, jid_=None, node=u""):
        """Tell if an entity has the required feature

        @param feature: feature namespace
        @param jid_: jid of the target, or None for profile's server
        @param node(unicode): optional node to use for disco request
        @return: a Deferred which fire a boolean (True if feature is available)
        """
        disco_infos = yield self.getInfos(client, jid_, node)
        defer.returnValue(feature in disco_infos.features)

    @defer.inlineCallbacks
    def checkFeature(self, client, feature, jid_=None, node=u""):
        """Like hasFeature, but raise an exception is feature is not Found

        @param feature: feature namespace
        @param jid_: jid of the target, or None for profile's server
        @param node(unicode): optional node to use for disco request

        @raise: exceptions.FeatureNotFound
        """
        disco_infos = yield self.getInfos(client, jid_, node)
        if not feature in disco_infos.features:
            raise failure.Failure(exceptions.FeatureNotFound)

    @defer.inlineCallbacks
    def checkFeatures(self, client, features, jid_=None, identity=None, node=u""):
        """Like checkFeature, but check several features at once, and check also identity

        @param features(iterable[unicode]): features to check
        @param jid_(jid.JID): jid of the target, or None for profile's server
        @param node(unicode): optional node to use for disco request
        @param identity(None, tuple(unicode, unicode): if not None, the entity must have an identity with this (category, type) tuple

        @raise: exceptions.FeatureNotFound
        """
        disco_infos = yield self.getInfos(client, jid_, node)
        if not set(features).issubset(disco_infos.features):
            raise failure.Failure(exceptions.FeatureNotFound())

        if identity is not None and identity not in disco_infos.identities:
            raise failure.Failure(exceptions.FeatureNotFound())

    def getInfos(self, client, jid_=None, node=u"", use_cache=True):
        """get disco infos from jid_, filling capability hash if needed

        @param jid_: jid of the target, or None for profile's server
        @param node(unicode): optional node to use for disco request
        @param use_cache(bool): if True, use cached data if available
        @return: a Deferred which fire disco.DiscoInfo
        """
        if jid_ is None:
            jid_ = jid.JID(client.jid.host)
        try:
            if not use_cache:
                # we ignore cache, so we pretend we haven't found it
                raise KeyError
            cap_hash = self.host.memory.getEntityData(
                jid_, [C.ENTITY_CAP_HASH], client.profile
            )[C.ENTITY_CAP_HASH]
        except (KeyError, exceptions.UnknownEntityError):
            # capability hash is not available, we'll compute one
            def infosCb(disco_infos):
                cap_hash = self.generateHash(disco_infos)
                self.hashes[cap_hash] = disco_infos
                self.host.memory.updateEntityData(
                    jid_, C.ENTITY_CAP_HASH, cap_hash, profile_key=client.profile
                )
                return disco_infos

            def infosEb(fail):
                if fail.check(defer.CancelledError):
                    reason = u"request time-out"
                    fail = failure.Failure(exceptions.TimeOutError(fail.message))
                else:
                    try:
                        reason = unicode(fail.value)
                    except AttributeError:
                        reason = unicode(fail)

                log.warning(
                    u"Error while requesting disco infos from {jid}: {reason}".format(
                        jid=jid_.full(), reason=reason
                    )
                )

                # XXX we set empty disco in cache, to avoid getting an error or waiting
                # for a timeout again the next time
                self.host.memory.updateEntityData(
                    jid_, C.ENTITY_CAP_HASH, CAP_HASH_ERROR, profile_key=client.profile
                )
                raise fail

            d = client.disco.requestInfo(jid_, nodeIdentifier=node)
            d.addCallback(infosCb)
            d.addErrback(infosEb)
            return d
        else:
            disco_infos = self.hashes[cap_hash]
            return defer.succeed(disco_infos)

    @defer.inlineCallbacks
    def getItems(self, client, jid_=None, node=u"", use_cache=True):
        """get disco items from jid_, cache them for our own server

        @param jid_(jid.JID): jid of the target, or None for profile's server
        @param node(unicode): optional node to use for disco request
        @param use_cache(bool): if True, use cached data if available
        @return: a Deferred which fire disco.DiscoItems
        """
        server_jid = jid.JID(client.jid.host)
        if jid_ is None:
            jid_ = server_jid

        if jid_ == server_jid and not node:
            # we cache items only for our own server and if node is not set
            try:
                items = self.host.memory.getEntityData(
                    jid_, ["DISCO_ITEMS"], client.profile
                )["DISCO_ITEMS"]
                log.debug(u"[%s] disco items are in cache" % jid_.full())
                if not use_cache:
                    # we ignore cache, so we pretend we haven't found it
                    raise KeyError
            except (KeyError, exceptions.UnknownEntityError):
                log.debug(u"Caching [%s] disco items" % jid_.full())
                items = yield client.disco.requestItems(jid_, nodeIdentifier=node)
                self.host.memory.updateEntityData(
                    jid_, "DISCO_ITEMS", items, profile_key=client.profile
                )
        else:
            try:
                items = yield client.disco.requestItems(jid_, nodeIdentifier=node)
            except StanzaError as e:
                log.warning(
                    u"Error while requesting items for {jid}: {reason}".format(
                        jid=jid_.full(), reason=e.condition
                    )
                )
                items = disco.DiscoItems()

        defer.returnValue(items)

    def _infosEb(self, failure_, entity_jid):
        failure_.trap(StanzaError)
        log.warning(
            _(u"Error while requesting [%(jid)s]: %(error)s")
            % {"jid": entity_jid.full(), "error": failure_.getErrorMessage()}
        )

    def findServiceEntity(self, client, category, type_, jid_=None):
        """Helper method to find first available entity from findServiceEntities

        args are the same as for [findServiceEntities]
        @return (jid.JID, None): found entity
        """
        d = self.host.findServiceEntities(client, "pubsub", "service")
        d.addCallback(lambda entities: entities.pop() if entities else None)
        return d

    def findServiceEntities(self, client, category, type_, jid_=None):
        """Return all available items of an entity which correspond to (category, type_)

        @param category: identity's category
        @param type_: identitiy's type
        @param jid_: the jid of the target server (None for profile's server)
        @return: a set of found entities
        @raise defer.CancelledError: the request timed out
        """
        found_entities = set()

        def infosCb(infos, entity_jid):
            if (category, type_) in infos.identities:
                found_entities.add(entity_jid)

        def gotItems(items):
            defers_list = []
            for item in items:
                info_d = self.getInfos(client, item.entity)
                info_d.addCallbacks(
                    infosCb, self._infosEb, [item.entity], None, [item.entity]
                )
                defers_list.append(info_d)
            return defer.DeferredList(defers_list)

        d = self.getItems(client, jid_)
        d.addCallback(gotItems)
        d.addCallback(lambda __: found_entities)
        reactor.callLater(
            TIMEOUT, d.cancel
        )  # FIXME: one bad service make a general timeout
        return d

    def findFeaturesSet(self, client, features, identity=None, jid_=None):
        """Return entities (including jid_ and its items) offering features

        @param features: iterable of features which must be present
        @param identity(None, tuple(unicode, unicode)): if not None, accept only this (category/type) identity
        @param jid_: the jid of the target server (None for profile's server)
        @param profile: %(doc_profile)s
        @return: a set of found entities
        """
        if jid_ is None:
            jid_ = jid.JID(client.jid.host)
        features = set(features)
        found_entities = set()

        def infosCb(infos, entity):
            if entity is None:
                log.warning(_(u"received an item without jid"))
                return
            if identity is not None and identity not in infos.identities:
                return
            if features.issubset(infos.features):
                found_entities.add(entity)

        def gotItems(items):
            defer_list = []
            for entity in [jid_] + [item.entity for item in items]:
                infos_d = self.getInfos(client, entity)
                infos_d.addCallbacks(infosCb, self._infosEb, [entity], None, [entity])
                defer_list.append(infos_d)
            return defer.DeferredList(defer_list)

        d = self.getItems(client, jid_)
        d.addCallback(gotItems)
        d.addCallback(lambda __: found_entities)
        reactor.callLater(
            TIMEOUT, d.cancel
        )  # FIXME: one bad service make a general timeout
        return d

    def generateHash(self, services):
        """ Generate a unique hash for given service

        hash algorithm is the one described in XEP-0115
        @param services: iterable of disco.DiscoIdentity/disco.DiscoFeature, as returned by discoHandler.info

        """
        s = []
        # identities
        byte_identities = [
            ByteIdentity(service)
            for service in services
            if isinstance(service, disco.DiscoIdentity)
        ]  # FIXME: lang must be managed here
        byte_identities.sort(key=lambda i: i.lang)
        byte_identities.sort(key=lambda i: i.idType)
        byte_identities.sort(key=lambda i: i.category)
        for identity in byte_identities:
            s.append(str(identity))
            s.append("<")
        # features
        byte_features = [
            service.encode("utf-8")
            for service in services
            if isinstance(service, disco.DiscoFeature)
        ]
        byte_features.sort()  # XXX: the default sort has the same behaviour as the requested RFC 4790 i;octet sort
        for feature in byte_features:
            s.append(feature)
            s.append("<")

        # extensions
        ext = services.extensions.values()
        ext.sort(key=lambda f: f.formNamespace.encode('utf-8'))
        for extension in ext:
            s.append(extension.formNamespace.encode('utf-8'))
            s.append("<")
            fields = extension.fieldList
            fields.sort(key=lambda f: f.var.encode('utf-8'))
            for field in fields:
                s.append(field.var.encode('utf-8'))
                s.append("<")
                values = [v.encode('utf-8') for v in field.values]
                values.sort()
                for value in values:
                    s.append(value)
                    s.append("<")

        cap_hash = b64encode(sha1("".join(s)).digest())
        log.debug(_(u"Capability hash generated: [{cap_hash}]").format(cap_hash=cap_hash))
        return cap_hash

    @defer.inlineCallbacks
    def _discoInfos(
        self, entity_jid_s, node=u"", use_cache=True, profile_key=C.PROF_KEY_NONE
    ):
        """ Discovery method for the bridge
        @param entity_jid_s: entity we want to discover
        @param use_cache(bool): if True, use cached data if available
        @param node(unicode): optional node to use

        @return: list of tuples
        """
        client = self.host.getClient(profile_key)
        entity = jid.JID(entity_jid_s)
        disco_infos = yield self.getInfos(client, entity, node, use_cache)
        extensions = {}
        # FIXME: should extensions be serialised using tools.common.data_format?
        for form_type, form in disco_infos.extensions.items():
            fields = []
            for field in form.fieldList:
                data = {"type": field.fieldType}
                for attr in ("var", "label", "desc"):
                    value = getattr(field, attr)
                    if value is not None:
                        data[attr] = value

                values = [field.value] if field.value is not None else field.values
                if field.fieldType == u"boolean":
                    values = [C.boolConst(C.bool(v)) for v in values]
                fields.append((data, values))

            extensions[form_type or ""] = fields

        defer.returnValue((
            disco_infos.features,
            [(cat, type_, name or "")
             for (cat, type_), name in disco_infos.identities.items()],
            extensions))

    def items2tuples(self, disco_items):
        """convert disco items to tuple of strings

        @param disco_items(iterable[disco.DiscoItem]): items
        @return G(tuple[unicode,unicode,unicode]): serialised items
        """
        for item in disco_items:
            if not item.entity:
                log.warning(_(u"invalid item (no jid)"))
                continue
            yield (item.entity.full(), item.nodeIdentifier or "", item.name or "")

    @defer.inlineCallbacks
    def _discoItems(
        self, entity_jid_s, node=u"", use_cache=True, profile_key=C.PROF_KEY_NONE
    ):
        """ Discovery method for the bridge

        @param entity_jid_s: entity we want to discover
        @param node(unicode): optional node to use
        @param use_cache(bool): if True, use cached data if available
        @return: list of tuples"""
        client = self.host.getClient(profile_key)
        entity = jid.JID(entity_jid_s)
        disco_items = yield self.getItems(client, entity, node, use_cache)
        ret = list(self.items2tuples(disco_items))
        defer.returnValue(ret)

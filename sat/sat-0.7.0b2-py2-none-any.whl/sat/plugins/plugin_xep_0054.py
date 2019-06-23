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
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.internet import threads, defer
from twisted.words.protocols.jabber import jid, error
from twisted.words.xish import domish
from twisted.python.failure import Failure

from zope.interface import implements

from wokkel import disco, iwokkel

from base64 import b64decode, b64encode
from hashlib import sha1
from sat.core import exceptions
from sat.memory import persistent
import mimetypes

try:
    from PIL import Image
except:
    raise exceptions.MissingModule(
        u"Missing module pillow, please download/install it from https://python-pillow.github.io"
    )
from cStringIO import StringIO

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

AVATAR_PATH = "avatars"
AVATAR_DIM = (64, 64)  #  FIXME: dim are not adapted to modern resolutions !

IQ_GET = '/iq[@type="get"]'
NS_VCARD = "vcard-temp"
VCARD_REQUEST = IQ_GET + '/vCard[@xmlns="' + NS_VCARD + '"]'  # TODO: manage requests

PRESENCE = "/presence"
NS_VCARD_UPDATE = "vcard-temp:x:update"
VCARD_UPDATE = PRESENCE + '/x[@xmlns="' + NS_VCARD_UPDATE + '"]'

CACHED_DATA = {"avatar", "nick"}
MAX_AGE = 60 * 60 * 24 * 365

PLUGIN_INFO = {
    C.PI_NAME: "XEP 0054 Plugin",
    C.PI_IMPORT_NAME: "XEP-0054",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0054", "XEP-0153"],
    C.PI_DEPENDENCIES: [],
    C.PI_RECOMMENDATIONS: ["XEP-0045"],
    C.PI_MAIN: "XEP_0054",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of vcard-temp"""),
}


class XEP_0054(object):
    # TODO: - check that nickname is ok
    #      - refactor the code/better use of Wokkel
    #      - get missing values

    def __init__(self, host):
        log.info(_(u"Plugin XEP_0054 initialization"))
        self.host = host
        host.bridge.addMethod(
            u"avatarGet",
            u".plugin",
            in_sign=u"sbbs",
            out_sign=u"s",
            method=self._getAvatar,
            async=True,
        )
        host.bridge.addMethod(
            u"avatarSet",
            u".plugin",
            in_sign=u"ss",
            out_sign=u"",
            method=self._setAvatar,
            async=True,
        )
        host.trigger.add(u"presence_available", self.presenceAvailableTrigger)
        host.memory.setSignalOnUpdate(u"avatar")
        host.memory.setSignalOnUpdate(u"nick")

    def getHandler(self, client):
        return XEP_0054_handler(self)

    def isRoom(self, client, entity_jid):
        """Tell if a jid is a MUC one

        @param entity_jid(jid.JID): full or bare jid of the entity check
        @return (bool): True if the bare jid of the entity is a room jid
        """
        try:
            muc_plg = self.host.plugins["XEP-0045"]
        except KeyError:
            return False

        try:
            muc_plg.checkRoomJoined(client, entity_jid.userhostJID())
        except exceptions.NotFound:
            return False
        else:
            return True

    def getBareOrFull(self, client, jid_):
        """use full jid if jid_ is an occupant of a room, bare jid else

        @param jid_(jid.JID): entity to test
        @return (jid.JID): bare or full jid
        """
        if jid_.resource:
            if not self.isRoom(client, jid_):
                return jid_.userhostJID()
        return jid_

    def presenceAvailableTrigger(self, presence_elt, client):
        if client.jid.userhost() in client._cache_0054:
            try:
                avatar_hash = client._cache_0054[client.jid.userhost()]["avatar"]
            except KeyError:
                log.info(u"No avatar in cache for {}".format(client.jid.userhost()))
                return True
            x_elt = domish.Element((NS_VCARD_UPDATE, "x"))
            x_elt.addElement("photo", content=avatar_hash)
            presence_elt.addChild(x_elt)
        return True

    @defer.inlineCallbacks
    def profileConnecting(self, client):
        client._cache_0054 = persistent.PersistentBinaryDict(NS_VCARD, client.profile)
        yield client._cache_0054.load()
        self._fillCachedValues(client.profile)

    def _fillCachedValues(self, profile):
        # FIXME: this may need to be reworked
        #       the current naive approach keeps a map between all jids
        #       in persistent cache, then put avatar hashs in memory.
        #       Hashes should be shared between profiles (or not ? what
        #       if the avatar is different depending on who is requesting it
        #       this is not possible with vcard-tmp, but it is with XEP-0084).
        #       Loading avatar on demand per jid may be an option to investigate.
        client = self.host.getClient(profile)
        for jid_s, data in client._cache_0054.iteritems():
            jid_ = jid.JID(jid_s)
            for name in CACHED_DATA:
                try:
                    value = data[name]
                    if value is None:
                        log.error(
                            u"{name} value for {jid_} is None, ignoring".format(
                                name=name, jid_=jid_
                            )
                        )
                        continue
                    self.host.memory.updateEntityData(
                        jid_, name, data[name], silent=True, profile_key=profile
                    )
                except KeyError:
                    pass

    def updateCache(self, client, jid_, name, value):
        """update cache value

        save value in memory in case of change
        @param jid_(jid.JID): jid of the owner of the vcard
        @param name(str): name of the item which changed
        @param value(unicode, None): new value of the item
            None to delete
        """
        jid_ = self.getBareOrFull(client, jid_)
        jid_s = jid_.full()

        if value is None:
            try:
                self.host.memory.delEntityDatum(jid_, name, client.profile)
            except (KeyError, exceptions.UnknownEntityError):
                pass
            if name in CACHED_DATA:
                try:
                    del client._cache_0054[jid_s][name]
                except KeyError:
                    pass
                else:
                    client._cache_0054.force(jid_s)
        else:
            self.host.memory.updateEntityData(
                jid_, name, value, profile_key=client.profile
            )
            if name in CACHED_DATA:
                client._cache_0054.setdefault(jid_s, {})[name] = value
                client._cache_0054.force(jid_s)

    def getCache(self, client, entity_jid, name):
        """return cached value for jid

        @param entity_jid(jid.JID): target contact
        @param name(unicode): name of the value ('nick' or 'avatar')
        @return(unicode, None): wanted value or None"""
        entity_jid = self.getBareOrFull(client, entity_jid)
        try:
            data = self.host.memory.getEntityData(entity_jid, [name], client.profile)
        except exceptions.UnknownEntityError:
            return None
        return data.get(name)

    def savePhoto(self, client, photo_elt, entity_jid):
        """Parse a <PHOTO> photo_elt and save the picture"""
        # XXX: this method is launched in a separate thread
        try:
            mime_type = unicode(photo_elt.elements(NS_VCARD, "TYPE").next())
        except StopIteration:
            log.warning(u"no MIME type found, assuming image/png")
            mime_type = u"image/png"
        else:
            if not mime_type:
                log.warning(u"empty MIME type, assuming image/png")
                mime_type = u"image/png"
            elif mime_type not in ("image/gif", "image/jpeg", "image/png"):
                if mime_type == "image/x-png":
                    # XXX: this old MIME type is still used by some clients
                    mime_type = "image/png"
                else:
                    # TODO: handle other image formats (svg?)
                    log.warning(
                        u"following avatar image format is not handled: {type} [{jid}]".format(
                            type=mime_type, jid=entity_jid.full()
                        )
                    )
                    raise Failure(exceptions.DataError())

            ext = mimetypes.guess_extension(mime_type, strict=False)
            assert ext is not None
            if ext == u".jpe":
                ext = u".jpg"
            log.debug(
                u"photo of type {type} with extension {ext} found [{jid}]".format(
                    type=mime_type, ext=ext, jid=entity_jid.full()
                )
            )
        try:
            buf = str(photo_elt.elements(NS_VCARD, "BINVAL").next())
        except StopIteration:
            log.warning(u"BINVAL element not found")
            raise Failure(exceptions.NotFound())
        if not buf:
            log.warning(u"empty avatar for {jid}".format(jid=entity_jid.full()))
            raise Failure(exceptions.NotFound())
        log.debug(_(u"Decoding binary"))
        decoded = b64decode(buf)
        del buf
        image_hash = sha1(decoded).hexdigest()
        with client.cache.cacheData(
            PLUGIN_INFO["import_name"],
            image_hash,
            mime_type,
            # we keep in cache for 1 year
            MAX_AGE,
        ) as f:
            f.write(decoded)
        return image_hash

    @defer.inlineCallbacks
    def vCard2Dict(self, client, vcard, entity_jid):
        """Convert a VCard to a dict, and save binaries"""
        log.debug((u"parsing vcard"))
        vcard_dict = {}

        for elem in vcard.elements():
            if elem.name == "FN":
                vcard_dict["fullname"] = unicode(elem)
            elif elem.name == "NICKNAME":
                vcard_dict["nick"] = unicode(elem)
                self.updateCache(client, entity_jid, "nick", vcard_dict["nick"])
            elif elem.name == "URL":
                vcard_dict["website"] = unicode(elem)
            elif elem.name == "EMAIL":
                vcard_dict["email"] = unicode(elem)
            elif elem.name == "BDAY":
                vcard_dict["birthday"] = unicode(elem)
            elif elem.name == "PHOTO":
                # TODO: handle EXTVAL
                try:
                    avatar_hash = yield threads.deferToThread(
                        self.savePhoto, client, elem, entity_jid
                    )
                except (exceptions.DataError, exceptions.NotFound) as e:
                    avatar_hash = ""
                    vcard_dict["avatar"] = avatar_hash
                except Exception as e:
                    log.error(u"avatar saving error: {}".format(e))
                    avatar_hash = None
                else:
                    vcard_dict["avatar"] = avatar_hash
                self.updateCache(client, entity_jid, "avatar", avatar_hash)
            else:
                log.debug(u"FIXME: [{}] VCard tag is not managed yet".format(elem.name))

        # if a data in cache doesn't exist anymore, we need to delete it
        # so we check CACHED_DATA no gotten (i.e. not in vcard_dict keys)
        # and we reset them
        for datum in CACHED_DATA.difference(vcard_dict.keys()):
            log.debug(
                u"reseting vcard datum [{datum}] for {entity}".format(
                    datum=datum, entity=entity_jid.full()
                )
            )
            self.updateCache(client, entity_jid, datum, None)

        defer.returnValue(vcard_dict)

    def _vCardCb(self, vcard_elt, to_jid, client):
        """Called after the first get IQ"""
        log.debug(_("VCard found"))
        iq_elt = vcard_elt.parent
        try:
            from_jid = jid.JID(iq_elt["from"])
        except KeyError:
            from_jid = client.jid.userhostJID()
        d = self.vCard2Dict(client, vcard_elt, from_jid)
        return d

    def _vCardEb(self, failure_, to_jid, client):
        """Called when something is wrong with registration"""
        log.warning(
            u"Can't get vCard for {jid}: {failure}".format(
                jid=to_jid.full, failure=failure_
            )
        )
        self.updateCache(client, to_jid, "avatar", None)

    def _getVcardElt(self, iq_elt):
        return iq_elt.elements(NS_VCARD, "vCard").next()

    def getCardRaw(self, client, entity_jid):
        """get raw vCard XML

        params are as in [getCard]
        """
        entity_jid = self.getBareOrFull(client, entity_jid)
        log.debug(u"Asking for {}'s VCard".format(entity_jid.full()))
        reg_request = client.IQ("get")
        reg_request["from"] = client.jid.full()
        reg_request["to"] = entity_jid.full()
        reg_request.addElement("vCard", NS_VCARD)
        d = reg_request.send(entity_jid.full())
        d.addCallback(self._getVcardElt)
        return d

    def getCard(self, client, entity_jid):
        """Ask server for VCard

        @param entity_jid(jid.JID): jid from which we want the VCard
        @result: id to retrieve the profile
        """
        d = self.getCardRaw(client, entity_jid)
        d.addCallbacks(
            self._vCardCb,
            self._vCardEb,
            callbackArgs=[entity_jid, client],
            errbackArgs=[entity_jid, client],
        )
        return d

    def _getCardCb(self, __, client, entity):
        try:
            return client._cache_0054[entity.full()]["avatar"]
        except KeyError:
            raise Failure(exceptions.NotFound())

    def _getAvatar(self, entity, cache_only, hash_only, profile):
        client = self.host.getClient(profile)
        d = self.getAvatar(client, jid.JID(entity), cache_only, hash_only)
        d.addErrback(lambda __: "")

        return d

    def getAvatar(self, client, entity, cache_only=True, hash_only=False):
        """get avatar full path or hash

        if avatar is not in local cache, it will be requested to the server
        @param entity(jid.JID): entity to get avatar from
        @param cache_only(bool): if False, will request vCard if avatar is
            not in cache
        @param hash_only(bool): if True only return hash, not full path
        @raise exceptions.NotFound: no avatar found
        """
        if not entity.resource and self.isRoom(client, entity):
            raise exceptions.NotFound
        entity = self.getBareOrFull(client, entity)
        full_path = None

        try:
            # we first check if we have avatar in cache
            avatar_hash = client._cache_0054[entity.full()]["avatar"]
            if avatar_hash:
                # avatar is known and exists
                full_path = client.cache.getFilePath(avatar_hash)
                if full_path is None:
                    # cache file is not available (probably expired)
                    raise KeyError
            else:
                # avatar has already been checked but it is not set
                full_path = u""
        except KeyError:
            # avatar is not in cache
            if cache_only:
                return defer.fail(Failure(exceptions.NotFound()))
            # we request vCard to get avatar
            d = self.getCard(client, entity)
            d.addCallback(self._getCardCb, client, entity)
        else:
            # avatar is in cache, we can return hash
            d = defer.succeed(avatar_hash)

        if not hash_only:
            # full path is requested
            if full_path is None:
                d.addCallback(client.cache.getFilePath)
            else:
                d.addCallback(lambda __: full_path)
        return d

    @defer.inlineCallbacks
    def getNick(self, client, entity):
        """get nick from cache, or check vCard

        @param entity(jid.JID): entity to get nick from
        @return(unicode, None): nick or None if not found
        """
        nick = self.getCache(client, entity, u"nick")
        if nick is not None:
            defer.returnValue(nick)
        yield self.getCard(client, entity)
        defer.returnValue(self.getCache(client, entity, u"nick"))

    @defer.inlineCallbacks
    def setNick(self, client, nick):
        """update our vCard and set a nickname

        @param nick(unicode): new nickname to use
        """
        jid_ = client.jid.userhostJID()
        try:
            vcard_elt = yield self.getCardRaw(client, jid_)
        except error.StanzaError as e:
            if e.condition == "item-not-found":
                vcard_elt = domish.Element((NS_VCARD, "vCard"))
            else:
                raise e
        try:
            nickname_elt = next(vcard_elt.elements(NS_VCARD, u"NICKNAME"))
        except StopIteration:
            pass
        else:
            vcard_elt.children.remove(nickname_elt)

        nickname_elt = vcard_elt.addElement((NS_VCARD, u"NICKNAME"), content=nick)
        iq_elt = client.IQ()
        vcard_elt = iq_elt.addChild(vcard_elt)
        yield iq_elt.send()
        self.updateCache(client, jid_, u"nick", unicode(nick))

    def _buildSetAvatar(self, client, vcard_elt, file_path):
        # XXX: this method is executed in a separate thread
        try:
            img = Image.open(file_path)
        except IOError:
            return Failure(exceptions.DataError(u"Can't open image"))

        if img.size != AVATAR_DIM:
            img.thumbnail(AVATAR_DIM)
            if img.size[0] != img.size[1]:  # we need to crop first
                left, upper = (0, 0)
                right, lower = img.size
                offset = abs(right - lower) / 2
                if right == min(img.size):
                    upper += offset
                    lower -= offset
                else:
                    left += offset
                    right -= offset
                img = img.crop((left, upper, right, lower))
        img_buf = StringIO()
        img.save(img_buf, "PNG")

        photo_elt = vcard_elt.addElement("PHOTO")
        photo_elt.addElement("TYPE", content="image/png")
        photo_elt.addElement("BINVAL", content=b64encode(img_buf.getvalue()))
        image_hash = sha1(img_buf.getvalue()).hexdigest()
        with client.cache.cacheData(
            PLUGIN_INFO["import_name"], image_hash, "image/png", MAX_AGE
        ) as f:
            f.write(img_buf.getvalue())
        return image_hash

    def _setAvatar(self, file_path, profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        return self.setAvatar(client, file_path)

    @defer.inlineCallbacks
    def setAvatar(self, client, file_path):
        """Set avatar of the profile

        @param file_path: path of the image of the avatar
        """
        try:
            # we first check if a vcard already exists, to keep data
            vcard_elt = yield self.getCardRaw(client, client.jid.userhostJID())
        except error.StanzaError as e:
            if e.condition == "item-not-found":
                vcard_elt = domish.Element((NS_VCARD, "vCard"))
            else:
                raise e
        else:
            # the vcard exists, we need to remove PHOTO element as we'll make a new one
            try:
                photo_elt = next(vcard_elt.elements(NS_VCARD, u"PHOTO"))
            except StopIteration:
                pass
            else:
                vcard_elt.children.remove(photo_elt)

        iq_elt = client.IQ()
        iq_elt.addChild(vcard_elt)
        image_hash = yield threads.deferToThread(
            self._buildSetAvatar, client, vcard_elt, file_path
        )
        # image is now at the right size/format

        self.updateCache(client, client.jid.userhostJID(), "avatar", image_hash)
        yield iq_elt.send()
        client.presence.available()  # FIXME: should send the current presence, not always "available" !


class XEP_0054_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        self.xmlstream.addObserver(VCARD_UPDATE, self.update)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_VCARD)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

    def _checkAvatarHash(self, __, client, entity, given_hash):
        """check that hash in cash (i.e. computed hash) is the same as given one"""
        # XXX: if they differ, the avater will be requested on each connection
        # TODO: try to avoid re-requesting avatar in this case
        computed_hash = self.plugin_parent.getCache(client, entity, "avatar")
        if computed_hash != given_hash:
            log.warning(
                u"computed hash differs from given hash for {entity}:\n"
                "computed: {computed}\ngiven: {given}".format(
                    entity=entity, computed=computed_hash, given=given_hash
                )
            )

    def update(self, presence):
        """Called on <presence/> stanza with vcard data

        Check for avatar information, and get VCard if needed
        @param presend(domish.Element): <presence/> stanza
        """
        client = self.parent
        entity_jid = self.plugin_parent.getBareOrFull(client, jid.JID(presence["from"]))
        # FIXME: wokkel's data_form should be used here
        try:
            x_elt = presence.elements(NS_VCARD_UPDATE, "x").next()
        except StopIteration:
            return

        try:
            photo_elt = x_elt.elements(NS_VCARD_UPDATE, "photo").next()
        except StopIteration:
            return

        hash_ = unicode(photo_elt).strip()
        if hash_ == C.HASH_SHA1_EMPTY:
            hash_ = u""
        old_avatar = self.plugin_parent.getCache(client, entity_jid, "avatar")

        if old_avatar == hash_:
            # no change, we can return...
            if hash_:
                # ...but we double check that avatar is in cache
                file_path = client.cache.getFilePath(hash_)
                if file_path is None:
                    log.error(
                        u"Avatar for [{}] should be in cache but it is not! We get it".format(
                            entity_jid.full()
                        )
                    )
                    self.plugin_parent.getCard(client, entity_jid)
            else:
                log.debug(u"avatar for {} already in cache".format(entity_jid.full()))
            return

        if not hash_:
            # the avatar has been removed
            # XXX: we use empty string instead of None to indicate that we took avatar
            #      but it is empty on purpose
            self.plugin_parent.updateCache(client, entity_jid, "avatar", "")
            return

        file_path = client.cache.getFilePath(hash_)
        if file_path is not None:
            log.debug(
                u"New avatar found for [{}], it's already in cache, we use it".format(
                    entity_jid.full()
                )
            )
            self.plugin_parent.updateCache(client, entity_jid, "avatar", hash_)
        else:
            log.debug(
                u"New avatar found for [{}], requesting vcard".format(entity_jid.full())
            )
            d = self.plugin_parent.getCard(client, entity_jid)
            d.addCallback(self._checkAvatarHash, client, entity_jid, hash_)

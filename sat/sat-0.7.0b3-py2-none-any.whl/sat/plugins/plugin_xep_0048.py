#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Bookmarks (xep-0048)
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
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.memory.persistent import PersistentBinaryDict
from sat.tools import xml_tools
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.error import StanzaError

from twisted.internet import defer

NS_BOOKMARKS = "storage:bookmarks"

PLUGIN_INFO = {
    C.PI_NAME: "Bookmarks",
    C.PI_IMPORT_NAME: "XEP-0048",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0048"],
    C.PI_DEPENDENCIES: ["XEP-0045"],
    C.PI_RECOMMENDATIONS: ["XEP-0049"],
    C.PI_MAIN: "XEP_0048",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of bookmarks"""),
}


class XEP_0048(object):
    MUC_TYPE = "muc"
    URL_TYPE = "url"
    MUC_KEY = "jid"
    URL_KEY = "url"
    MUC_ATTRS = ("autojoin", "name")
    URL_ATTRS = ("name",)

    def __init__(self, host):
        log.info(_("Bookmarks plugin initialization"))
        self.host = host
        # self.__menu_id = host.registerCallback(self._bookmarksMenu, with_data=True)
        self.__bm_save_id = host.registerCallback(self._bookmarksSaveCb, with_data=True)
        host.importMenu(
            (D_("Groups"), D_("Bookmarks")),
            self._bookmarksMenu,
            security_limit=0,
            help_string=D_("Use and manage bookmarks"),
        )
        self.__selected_id = host.registerCallback(
            self._bookmarkSelectedCb, with_data=True
        )
        host.bridge.addMethod(
            "bookmarksList",
            ".plugin",
            in_sign="sss",
            out_sign="a{sa{sa{ss}}}",
            method=self._bookmarksList,
            async=True,
        )
        host.bridge.addMethod(
            "bookmarksRemove",
            ".plugin",
            in_sign="ssss",
            out_sign="",
            method=self._bookmarksRemove,
            async=True,
        )
        host.bridge.addMethod(
            "bookmarksAdd",
            ".plugin",
            in_sign="ssa{ss}ss",
            out_sign="",
            method=self._bookmarksAdd,
            async=True,
        )
        try:
            self.private_plg = self.host.plugins["XEP-0049"]
        except KeyError:
            self.private_plg = None
        try:
            self.host.plugins[C.TEXT_CMDS].registerTextCommands(self)
        except KeyError:
            log.info(_("Text commands not available"))

    @defer.inlineCallbacks
    def profileConnected(self, client):
        local = client.bookmarks_local = PersistentBinaryDict(
            NS_BOOKMARKS, client.profile
        )
        yield local.load()
        if not local:
            local[XEP_0048.MUC_TYPE] = dict()
            local[XEP_0048.URL_TYPE] = dict()
        private = yield self._getServerBookmarks("private", client.profile)
        pubsub = client.bookmarks_pubsub = None

        for bookmarks in (local, private, pubsub):
            if bookmarks is not None:
                for (room_jid, data) in bookmarks[XEP_0048.MUC_TYPE].items():
                    if data.get("autojoin", "false") == "true":
                        nick = data.get("nick", client.jid.user)
                        self.host.plugins["XEP-0045"].join(client, room_jid, nick, {})

    @defer.inlineCallbacks
    def _getServerBookmarks(self, storage_type, profile):
        """Get distants bookmarks

        update also the client.bookmarks_[type] key, with None if service is not available
        @param storage_type: storage type, can be:
            - 'private': XEP-0049 storage
            - 'pubsub': XEP-0223 storage
        @param profile: %(doc_profile)s
        @return: data dictionary, or None if feature is not available
        """
        client = self.host.getClient(profile)
        if storage_type == "private":
            try:
                bookmarks_private_xml = yield self.private_plg.privateXMLGet(
                    "storage", NS_BOOKMARKS, profile
                )
                data = client.bookmarks_private = self._bookmarkElt2Dict(
                    bookmarks_private_xml
                )
            except (StanzaError, AttributeError):
                log.info(_("Private XML storage not available"))
                data = client.bookmarks_private = None
        elif storage_type == "pubsub":
            raise NotImplementedError
        else:
            raise ValueError("storage_type must be 'private' or 'pubsub'")
        defer.returnValue(data)

    @defer.inlineCallbacks
    def _setServerBookmarks(self, storage_type, bookmarks_elt, profile):
        """Save bookmarks on server

        @param storage_type: storage type, can be:
            - 'private': XEP-0049 storage
            - 'pubsub': XEP-0223 storage
        @param bookmarks_elt (domish.Element): bookmarks XML
        @param profile: %(doc_profile)s
        """
        if storage_type == "private":
            yield self.private_plg.privateXMLStore(bookmarks_elt, profile)
        elif storage_type == "pubsub":
            raise NotImplementedError
        else:
            raise ValueError("storage_type must be 'private' or 'pubsub'")

    def _bookmarkElt2Dict(self, storage_elt):
        """Parse bookmarks to get dictionary
        @param storage_elt (domish.Element): bookmarks storage
        @return (dict): bookmark data (key: bookmark type, value: list) where key can be:
            - XEP_0048.MUC_TYPE
            - XEP_0048.URL_TYPE
            - value (dict): data as for addBookmark
        """
        conf_data = {}
        url_data = {}

        conference_elts = storage_elt.elements(NS_BOOKMARKS, "conference")
        for conference_elt in conference_elts:
            try:
                room_jid = jid.JID(conference_elt[XEP_0048.MUC_KEY])
            except KeyError:
                log.warning(
                    "invalid bookmark found, igoring it:\n%s" % conference_elt.toXml()
                )
                continue

            data = conf_data[room_jid] = {}

            for attr in XEP_0048.MUC_ATTRS:
                if conference_elt.hasAttribute(attr):
                    data[attr] = conference_elt[attr]
            try:
                data["nick"] = unicode(
                    conference_elt.elements(NS_BOOKMARKS, "nick").next()
                )
            except StopIteration:
                pass
            # TODO: manage password (need to be secured, see XEP-0049 §4)

        url_elts = storage_elt.elements(NS_BOOKMARKS, "url")
        for url_elt in url_elts:
            try:
                url = url_elt[XEP_0048.URL_KEY]
            except KeyError:
                log.warning("invalid bookmark found, igoring it:\n%s" % url_elt.toXml())
                continue
            data = url_data[url] = {}
            for attr in XEP_0048.URL_ATTRS:
                if url_elt.hasAttribute(attr):
                    data[attr] = url_elt[attr]

        return {XEP_0048.MUC_TYPE: conf_data, XEP_0048.URL_TYPE: url_data}

    def _dict2BookmarkElt(self, type_, data):
        """Construct a bookmark element from a data dict
        @param data (dict): bookmark data (key: bookmark type, value: list) where key can be:
            - XEP_0048.MUC_TYPE
            - XEP_0048.URL_TYPE
            - value (dict): data as for addBookmark
        @return (domish.Element): bookmark element
        """
        rooms_data = data.get(XEP_0048.MUC_TYPE, {})
        urls_data = data.get(XEP_0048.URL_TYPE, {})
        storage_elt = domish.Element((NS_BOOKMARKS, "storage"))
        for room_jid in rooms_data:
            conference_elt = storage_elt.addElement("conference")
            conference_elt[XEP_0048.MUC_KEY] = room_jid.full()
            for attr in XEP_0048.MUC_ATTRS:
                try:
                    conference_elt[attr] = rooms_data[room_jid][attr]
                except KeyError:
                    pass
            try:
                conference_elt.addElement("nick", content=rooms_data[room_jid]["nick"])
            except KeyError:
                pass

        for url in urls_data:
            url_elt = storage_elt.addElement("url")
            url_elt[XEP_0048.URL_KEY] = url
            for attr in XEP_0048.URL_ATTRS:
                try:
                    url_elt[attr] = url[attr]
                except KeyError:
                    pass

        return storage_elt

    def _bookmarkSelectedCb(self, data, profile):
        try:
            room_jid_s, nick = data["index"].split(" ", 1)
            room_jid = jid.JID(room_jid_s)
        except (KeyError, RuntimeError):
            log.warning(_("No room jid selected"))
            return {}

        client = self.host.getClient(profile)
        d = self.host.plugins["XEP-0045"].join(client, room_jid, nick, {})

        def join_eb(failure):
            log.warning(u"Error while trying to join room: {}".format(failure))
            # FIXME: failure are badly managed in plugin XEP-0045. Plugin XEP-0045 need to be fixed before managing errors correctly here
            return {}

        d.addCallbacks(lambda __: {}, join_eb)
        return d

    def _bookmarksMenu(self, data, profile):
        """ XMLUI activated by menu: return Gateways UI
        @param profile: %(doc_profile)s

        """
        client = self.host.getClient(profile)
        xmlui = xml_tools.XMLUI(title=_("Bookmarks manager"))
        adv_list = xmlui.changeContainer(
            "advanced_list",
            columns=3,
            selectable="single",
            callback_id=self.__selected_id,
        )
        for bookmarks in (
            client.bookmarks_local,
            client.bookmarks_private,
            client.bookmarks_pubsub,
        ):
            if bookmarks is None:
                continue
            for (room_jid, data) in sorted(
                bookmarks[XEP_0048.MUC_TYPE].items(),
                key=lambda item: item[1].get("name", item[0].user),
            ):
                room_jid_s = room_jid.full()
                adv_list.setRowIndex(
                    u"%s %s" % (room_jid_s, data.get("nick") or client.jid.user)
                )
                xmlui.addText(data.get("name", ""))
                xmlui.addJid(room_jid)
                if C.bool(data.get("autojoin", C.BOOL_FALSE)):
                    xmlui.addText("autojoin")
                else:
                    xmlui.addEmpty()
        adv_list.end()
        xmlui.addDivider("dash")
        xmlui.addText(_("add a bookmark"))
        xmlui.changeContainer("pairs")
        xmlui.addLabel(_("Name"))
        xmlui.addString("name")
        xmlui.addLabel(_("jid"))
        xmlui.addString("jid")
        xmlui.addLabel(_("Nickname"))
        xmlui.addString("nick", client.jid.user)
        xmlui.addLabel(_("Autojoin"))
        xmlui.addBool("autojoin")
        xmlui.changeContainer("vertical")
        xmlui.addButton(self.__bm_save_id, _("Save"), ("name", "jid", "nick", "autojoin"))
        return {"xmlui": xmlui.toXml()}

    def _bookmarksSaveCb(self, data, profile):
        bm_data = xml_tools.XMLUIResult2DataFormResult(data)
        try:
            location = jid.JID(bm_data.pop("jid"))
        except KeyError:
            raise exceptions.InternalError("Can't find mandatory key")
        d = self.addBookmark(XEP_0048.MUC_TYPE, location, bm_data, profile_key=profile)
        d.addCallback(lambda __: {})
        return d

    @defer.inlineCallbacks
    def addBookmark(
        self, type_, location, data, storage_type="auto", profile_key=C.PROF_KEY_NONE
    ):
        """Store a new bookmark

        @param type_: bookmark type, one of:
            - XEP_0048.MUC_TYPE: Multi-User chat room
            - XEP_0048.URL_TYPE: web page URL
        @param location: dependeding on type_, can be a MUC room jid or an url
        @param data (dict): depending on type_, can contains the following keys:
            - name: human readable name of the bookmark
            - nick: user preferred room nick (default to user part of profile's jid)
            - autojoin: "true" if room must be automatically joined on connection
            - password: unused yet TODO
        @param storage_type: where the bookmark will be stored, can be:
            - "auto": find best available option: pubsub, private, local in that order
            - "pubsub": PubSub private storage (XEP-0223)
            - "private": Private XML storage (XEP-0049)
            - "local": Store in SàT database
        @param profile_key: %(doc_profile_key)s
        """
        assert storage_type in ("auto", "pubsub", "private", "local")
        if type_ == XEP_0048.URL_TYPE and {"autojoin", "nick"}.intersection(data.keys()):
            raise ValueError("autojoin or nick can't be used with URLs")
        client = self.host.getClient(profile_key)
        if storage_type == "auto":
            if client.bookmarks_pubsub is not None:
                storage_type = "pubsub"
            elif client.bookmarks_private is not None:
                storage_type = "private"
            else:
                storage_type = "local"
                log.warning(_("Bookmarks will be local only"))
            log.info(_('Type selected for "auto" storage: %s') % storage_type)

        if storage_type == "local":
            client.bookmarks_local[type_][location] = data
            yield client.bookmarks_local.force(type_)
        else:
            bookmarks = yield self._getServerBookmarks(storage_type, client.profile)
            bookmarks[type_][location] = data
            bookmark_elt = self._dict2BookmarkElt(type_, bookmarks)
            yield self._setServerBookmarks(storage_type, bookmark_elt, client.profile)

    @defer.inlineCallbacks
    def removeBookmark(
        self, type_, location, storage_type="all", profile_key=C.PROF_KEY_NONE
    ):
        """Remove a stored bookmark

        @param type_: bookmark type, one of:
            - XEP_0048.MUC_TYPE: Multi-User chat room
            - XEP_0048.URL_TYPE: web page URL
        @param location: dependeding on type_, can be a MUC room jid or an url
        @param storage_type: where the bookmark is stored, can be:
            - "all": remove from everywhere
            - "pubsub": PubSub private storage (XEP-0223)
            - "private": Private XML storage (XEP-0049)
            - "local": Store in SàT database
        @param profile_key: %(doc_profile_key)s
        """
        assert storage_type in ("all", "pubsub", "private", "local")
        client = self.host.getClient(profile_key)

        if storage_type in ("all", "local"):
            try:
                del client.bookmarks_local[type_][location]
                yield client.bookmarks_local.force(type_)
            except KeyError:
                log.debug("Bookmark is not present in local storage")

        if storage_type in ("all", "private"):
            bookmarks = yield self._getServerBookmarks("private", client.profile)
            try:
                del bookmarks[type_][location]
                bookmark_elt = self._dict2BookmarkElt(type_, bookmarks)
                yield self._setServerBookmarks("private", bookmark_elt, client.profile)
            except KeyError:
                log.debug("Bookmark is not present in private storage")

        if storage_type == "pubsub":
            raise NotImplementedError

    def _bookmarksList(self, type_, storage_location, profile_key=C.PROF_KEY_NONE):
        """Return stored bookmarks

        @param type_: bookmark type, one of:
            - XEP_0048.MUC_TYPE: Multi-User chat room
            - XEP_0048.URL_TYPE: web page URL
        @param storage_location: can be:
            - 'all'
            - 'local'
            - 'private'
            - 'pubsub'
        @param profile_key: %(doc_profile_key)s
        @param return (dict): (key: storage_location, value dict) with:
            - value (dict): (key: bookmark_location, value: bookmark data)
        """
        client = self.host.getClient(profile_key)
        ret = {}
        ret_d = defer.succeed(ret)

        def fillBookmarks(__, _storage_location):
            bookmarks_ori = getattr(client, "bookmarks_" + _storage_location)
            if bookmarks_ori is None:
                return ret
            data = bookmarks_ori[type_]
            for bookmark in data:
                ret[_storage_location][bookmark.full()] = data[bookmark].copy()
            return ret

        for _storage_location in ("local", "private", "pubsub"):
            if storage_location in ("all", _storage_location):
                ret[_storage_location] = {}
                if _storage_location in ("private",):
                    # we update distant bookmarks, just in case an other client added something
                    d = self._getServerBookmarks(_storage_location, client.profile)
                else:
                    d = defer.succeed(None)
                d.addCallback(fillBookmarks, _storage_location)
                ret_d.addCallback(lambda __: d)

        return ret_d

    def _bookmarksRemove(
        self, type_, location, storage_location, profile_key=C.PROF_KEY_NONE
    ):
        """Return stored bookmarks

        @param type_: bookmark type, one of:
            - XEP_0048.MUC_TYPE: Multi-User chat room
            - XEP_0048.URL_TYPE: web page URL
        @param location: dependeding on type_, can be a MUC room jid or an url
        @param storage_location: can be:
            - "all": remove from everywhere
            - "pubsub": PubSub private storage (XEP-0223)
            - "private": Private XML storage (XEP-0049)
            - "local": Store in SàT database
        @param profile_key: %(doc_profile_key)s
        """
        if type_ == XEP_0048.MUC_TYPE:
            location = jid.JID(location)
        return self.removeBookmark(type_, location, storage_location, profile_key)

    def _bookmarksAdd(
        self, type_, location, data, storage_type="auto", profile_key=C.PROF_KEY_NONE
    ):
        if type_ == XEP_0048.MUC_TYPE:
            location = jid.JID(location)
        return self.addBookmark(type_, location, data, storage_type, profile_key)

    def cmd_bookmark(self, client, mess_data):
        """(Un)bookmark a MUC room

        @command (group): [autojoin | remove]
            - autojoin: join room automatically on connection
            - remove: remove bookmark(s) for this room
        """
        txt_cmd = self.host.plugins[C.TEXT_CMDS]

        options = mess_data["unparsed"].strip().split()
        if options and options[0] not in ("autojoin", "remove"):
            txt_cmd.feedBack(client, _("Bad arguments"), mess_data)
            return False

        room_jid = mess_data["to"].userhostJID()

        if "remove" in options:
            self.removeBookmark(XEP_0048.MUC_TYPE, room_jid, profile_key=client.profile)
            txt_cmd.feedBack(
                client,
                _("All [%s] bookmarks are being removed") % room_jid.full(),
                mess_data,
            )
            return False

        data = {
            "name": room_jid.user,
            "nick": client.jid.user,
            "autojoin": "true" if "autojoin" in options else "false",
        }
        self.addBookmark(XEP_0048.MUC_TYPE, room_jid, data, profile_key=client.profile)
        txt_cmd.feedBack(client, _("Bookmark added"), mess_data)

        return False

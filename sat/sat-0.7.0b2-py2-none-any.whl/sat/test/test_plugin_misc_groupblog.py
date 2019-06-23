#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

""" Plugin groupblogs """

from constants import Const as C
from sat.test import helpers, helpers_plugins
from sat.plugins import plugin_misc_groupblog
from sat.plugins import plugin_xep_0060
from sat.plugins import plugin_xep_0277
from sat.plugins import plugin_xep_0163
from sat.plugins import plugin_misc_text_syntaxes
from twisted.internet import defer
from twisted.words.protocols.jabber import jid


NS_PUBSUB = "http://jabber.org/protocol/pubsub"

DO_NOT_COUNT_COMMENTS = -1

SERVICE = u"pubsub.example.com"
PUBLISHER = u"test@example.org"
OTHER_PUBLISHER = u"other@xmpp.net"
NODE_ID = u"urn:xmpp:groupblog:{publisher}".format(publisher=PUBLISHER)
OTHER_NODE_ID = u"urn:xmpp:groupblog:{publisher}".format(publisher=OTHER_PUBLISHER)
ITEM_ID_1 = u"c745a688-9b02-11e3-a1a3-c0143dd4fe51"
COMMENT_ID_1 = u"d745a688-9b02-11e3-a1a3-c0143dd4fe52"
COMMENT_ID_2 = u"e745a688-9b02-11e3-a1a3-c0143dd4fe53"


def COMMENTS_NODE_ID(publisher=PUBLISHER):
    return u"urn:xmpp:comments:_{id}__urn:xmpp:groupblog:{publisher}".format(
        id=ITEM_ID_1, publisher=publisher
    )


def COMMENTS_NODE_URL(publisher=PUBLISHER):
    return u"xmpp:{service}?node={node}".format(
        service=SERVICE,
        id=ITEM_ID_1,
        node=COMMENTS_NODE_ID(publisher).replace(":", "%3A").replace("@", "%40"),
    )


def ITEM(publisher=PUBLISHER):
    return u"""
          <item id='{id}' xmlns='{ns}'>
            <entry>
              <title type='text'>The Uses of This World</title>
              <id>{id}</id>
              <updated>2003-12-12T17:47:23Z</updated>
              <published>2003-12-12T17:47:23Z</published>
              <link href='{comments_node_url}' rel='replies' title='comments'/>
              <author>
                <name>{publisher}</name>
              </author>
            </entry>
          </item>
        """.format(
        ns=NS_PUBSUB,
        id=ITEM_ID_1,
        publisher=publisher,
        comments_node_url=COMMENTS_NODE_URL(publisher),
    )


def COMMENT(id_=COMMENT_ID_1):
    return u"""
          <item id='{id}' xmlns='{ns}'>
            <entry>
              <title type='text'>The Uses of This World</title>
              <id>{id}</id>
              <updated>2003-12-12T17:47:23Z</updated>
              <published>2003-12-12T17:47:23Z</published>
              <author>
                <name>{publisher}</name>
              </author>
            </entry>
          </item>
        """.format(
        ns=NS_PUBSUB, id=id_, publisher=PUBLISHER
    )


def ITEM_DATA(id_=ITEM_ID_1, count=0):
    res = {
        "id": ITEM_ID_1,
        "type": "main_item",
        "content": "The Uses of This World",
        "author": PUBLISHER,
        "updated": "1071251243.0",
        "published": "1071251243.0",
        "service": SERVICE,
        "comments": COMMENTS_NODE_URL_1,
        "comments_service": SERVICE,
        "comments_node": COMMENTS_NODE_ID_1,
    }
    if count != DO_NOT_COUNT_COMMENTS:
        res.update({"comments_count": unicode(count)})
    return res


def COMMENT_DATA(id_=COMMENT_ID_1):
    return {
        "id": id_,
        "type": "comment",
        "content": "The Uses of This World",
        "author": PUBLISHER,
        "updated": "1071251243.0",
        "published": "1071251243.0",
        "service": SERVICE,
        "node": COMMENTS_NODE_ID_1,
        "verified_publisher": "false",
    }


COMMENTS_NODE_ID_1 = COMMENTS_NODE_ID()
COMMENTS_NODE_ID_2 = COMMENTS_NODE_ID(OTHER_PUBLISHER)
COMMENTS_NODE_URL_1 = COMMENTS_NODE_URL()
COMMENTS_NODE_URL_2 = COMMENTS_NODE_URL(OTHER_PUBLISHER)
ITEM_1 = ITEM()
ITEM_2 = ITEM(OTHER_PUBLISHER)
COMMENT_1 = COMMENT(COMMENT_ID_1)
COMMENT_2 = COMMENT(COMMENT_ID_2)


def ITEM_DATA_1(count=0):
    return ITEM_DATA(count=count)


COMMENT_DATA_1 = COMMENT_DATA()
COMMENT_DATA_2 = COMMENT_DATA(COMMENT_ID_2)


class XEP_groupblogTest(helpers.SatTestCase):
    def setUp(self):
        self.host = helpers.FakeSAT()
        self.host.plugins["XEP-0060"] = plugin_xep_0060.XEP_0060(self.host)
        self.host.plugins["XEP-0163"] = plugin_xep_0163.XEP_0163(self.host)
        reload(plugin_misc_text_syntaxes)  # reload the plugin to avoid conflict error
        self.host.plugins["TEXT_SYNTAXES"] = plugin_misc_text_syntaxes.TextSyntaxes(
            self.host
        )
        self.host.plugins["XEP-0277"] = plugin_xep_0277.XEP_0277(self.host)
        self.plugin = plugin_misc_groupblog.GroupBlog(self.host)
        self.plugin._initialise = self._initialise
        self.__initialised = False
        self._initialise(C.PROFILE[0])

    def _initialise(self, profile_key):
        profile = profile_key
        client = self.host.getClient(profile)
        if not self.__initialised:
            client.item_access_pubsub = jid.JID(SERVICE)
            xep_0060 = self.host.plugins["XEP-0060"]
            client.pubsub_client = helpers_plugins.FakeSatPubSubClient(
                self.host, xep_0060
            )
            client.pubsub_client.parent = client
            self.psclient = client.pubsub_client
            helpers.FakeSAT.getDiscoItems = self.psclient.service_getDiscoItems
            self.__initialised = True
        return defer.succeed((profile, client))

    def _addItem(self, profile, item, parent_node=None):
        client = self.host.getClient(profile)
        client.pubsub_client._addItem(item, parent_node)

    def test_sendGroupBlog(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.items(SERVICE, NODE_ID)
        d.addCallback(lambda items: self.assertEqual(len(items), 0))
        d.addCallback(
            lambda __: self.plugin.sendGroupBlog(
                "PUBLIC", [], "test", {}, C.PROFILE[0]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        return d.addCallback(lambda items: self.assertEqual(len(items), 1))

    def test_deleteGroupBlog(self):
        pub_data = (SERVICE, NODE_ID, ITEM_ID_1)
        self.host.bridge.expectCall(
            "personalEvent",
            C.JID_STR[0],
            "MICROBLOG_DELETE",
            {"type": "main_item", "id": ITEM_ID_1},
            C.PROFILE[0],
        )

        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.deleteGroupBlog(
                pub_data, COMMENTS_NODE_URL_1, profile_key=C.PROFILE[0]
            )
        )
        return d.addCallback(self.assertEqual, None)

    def test_updateGroupBlog(self):
        pub_data = (SERVICE, NODE_ID, ITEM_ID_1)
        new_text = u"silfu23RFWUP)IWNOEIOEFÖ"

        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.updateGroupBlog(
                pub_data, COMMENTS_NODE_URL_1, new_text, {}, profile_key=C.PROFILE[0]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        return d.addCallback(
            lambda items: self.assertEqual(
                "".join(items[0].entry.title.children), new_text
            )
        )

    def test_sendGroupBlogComment(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.items(SERVICE, NODE_ID)
        d.addCallback(lambda items: self.assertEqual(len(items), 0))
        d.addCallback(
            lambda __: self.plugin.sendGroupBlogComment(
                COMMENTS_NODE_URL_1, "test", {}, profile_key=C.PROFILE[0]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_1))
        return d.addCallback(lambda items: self.assertEqual(len(items), 1))

    def test_getGroupBlogs(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.getGroupBlogs(PUBLISHER, profile_key=C.PROFILE[0])
        )
        result = (
            [ITEM_DATA_1()],
            {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
        )
        return d.addCallback(self.assertEqual, result)

    def test_getGroupBlogsNoCount(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.getGroupBlogs(
                PUBLISHER, count_comments=False, profile_key=C.PROFILE[0]
            )
        )
        result = (
            [ITEM_DATA_1(DO_NOT_COUNT_COMMENTS)],
            {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
        )
        return d.addCallback(self.assertEqual, result)

    def test_getGroupBlogsWithIDs(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.getGroupBlogs(
                PUBLISHER, [ITEM_ID_1], profile_key=C.PROFILE[0]
            )
        )
        result = (
            [ITEM_DATA_1()],
            {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
        )
        return d.addCallback(self.assertEqual, result)

    def test_getGroupBlogsWithRSM(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.getGroupBlogs(
                PUBLISHER, rsm_data={"max_": 1}, profile_key=C.PROFILE[0]
            )
        )
        result = (
            [ITEM_DATA_1()],
            {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
        )
        return d.addCallback(self.assertEqual, result)

    def test_getGroupBlogsWithComments(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.psclient.publish(SERVICE, COMMENTS_NODE_ID_1, [COMMENT_1])
        )
        d.addCallback(
            lambda __: self.plugin.getGroupBlogsWithComments(
                PUBLISHER, [], profile_key=C.PROFILE[0]
            )
        )
        result = (
            [
                (
                    ITEM_DATA_1(1),
                    (
                        [COMMENT_DATA_1],
                        {
                            "count": "1",
                            "index": "0",
                            "first": COMMENT_ID_1,
                            "last": COMMENT_ID_1,
                        },
                    ),
                )
            ],
            {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
        )
        return d.addCallback(self.assertEqual, result)

    def test_getGroupBlogsWithComments2(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_1, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(
            lambda __: self.plugin.getGroupBlogsWithComments(
                PUBLISHER, [], profile_key=C.PROFILE[0]
            )
        )
        result = (
            [
                (
                    ITEM_DATA_1(2),
                    (
                        [COMMENT_DATA_1, COMMENT_DATA_2],
                        {
                            "count": "2",
                            "index": "0",
                            "first": COMMENT_ID_1,
                            "last": COMMENT_ID_2,
                        },
                    ),
                )
            ],
            {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
        )

        return d.addCallback(self.assertEqual, result)

    def test_getGroupBlogsAtom(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.getGroupBlogsAtom(
                PUBLISHER, {"max_": 1}, profile_key=C.PROFILE[0]
            )
        )

        def cb(atom):
            self.assertIsInstance(atom, unicode)
            self.assertTrue(atom.startswith('<?xml version="1.0" encoding="utf-8"?>'))

        return d.addCallback(cb)

    def test_getMassiveGroupBlogs(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.plugin.getMassiveGroupBlogs(
                "JID", [jid.JID(PUBLISHER)], {"max_": 1}, profile_key=C.PROFILE[0]
            )
        )
        result = {
            PUBLISHER: (
                [ITEM_DATA_1()],
                {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
            )
        }

        def clean(res):
            del self.host.plugins["XEP-0060"].node_cache[
                C.PROFILE[0] + "@found@" + SERVICE
            ]
            return res

        d.addCallback(clean)
        d.addCallback(self.assertEqual, result)

    def test_getMassiveGroupBlogsWithComments(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_1, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(
            lambda __: self.plugin.getMassiveGroupBlogs(
                "JID", [jid.JID(PUBLISHER)], {"max_": 1}, profile_key=C.PROFILE[0]
            )
        )
        result = {
            PUBLISHER: (
                [ITEM_DATA_1(2)],
                {"count": "1", "index": "0", "first": ITEM_ID_1, "last": ITEM_ID_1},
            )
        }

        def clean(res):
            del self.host.plugins["XEP-0060"].node_cache[
                C.PROFILE[0] + "@found@" + SERVICE
            ]
            return res

        d.addCallback(clean)
        d.addCallback(self.assertEqual, result)

    def test_getGroupBlogComments(self):
        self._initialise(C.PROFILE[0])
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.psclient.publish(SERVICE, COMMENTS_NODE_ID_1, [COMMENT_1])
        )
        d.addCallback(
            lambda __: self.plugin.getGroupBlogComments(
                SERVICE, COMMENTS_NODE_ID_1, {"max_": 1}, profile_key=C.PROFILE[0]
            )
        )
        result = (
            [COMMENT_DATA_1],
            {"count": "1", "index": "0", "first": COMMENT_ID_1, "last": COMMENT_ID_1},
        )
        return d.addCallback(self.assertEqual, result)

    def test_subscribeGroupBlog(self):
        self._initialise(C.PROFILE[0])
        d = self.plugin.subscribeGroupBlog(PUBLISHER, profile_key=C.PROFILE[0])
        return d.addCallback(self.assertEqual, None)

    def test_massiveSubscribeGroupBlogs(self):
        self._initialise(C.PROFILE[0])
        d = self.plugin.massiveSubscribeGroupBlogs(
            "JID", [jid.JID(PUBLISHER)], profile_key=C.PROFILE[0]
        )

        def clean(res):
            del self.host.plugins["XEP-0060"].node_cache[
                C.PROFILE[0] + "@found@" + SERVICE
            ]
            del self.host.plugins["XEP-0060"].node_cache[
                C.PROFILE[0] + "@subscriptions@" + SERVICE
            ]
            return res

        d.addCallback(clean)
        return d.addCallback(self.assertEqual, None)

    def test_deleteAllGroupBlogs(self):
        """Delete our main node and associated comments node"""
        self._initialise(C.PROFILE[0])
        self.host.profiles[C.PROFILE[0]].roster.addItem(jid.JID(OTHER_PUBLISHER))
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_1, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_1))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))

        d.addCallback(
            lambda __: self.psclient.publish(SERVICE, OTHER_NODE_ID, [ITEM_2])
        )
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_2, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, OTHER_NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_2))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))

        def clean(res):
            del self.host.plugins["XEP-0060"].node_cache[
                C.PROFILE[0] + "@found@" + SERVICE
            ]
            return res

        d.addCallback(lambda __: self.plugin.deleteAllGroupBlogs(C.PROFILE[0]))
        d.addCallback(clean)

        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 0))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_1))
        d.addCallback(lambda items: self.assertEqual(len(items), 0))

        d.addCallback(lambda __: self.psclient.items(SERVICE, OTHER_NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_2))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))
        return d

    def test_deleteAllGroupBlogsComments(self):
        """Delete the comments we posted on other node's"""
        self._initialise(C.PROFILE[0])
        self.host.profiles[C.PROFILE[0]].roster.addItem(jid.JID(OTHER_PUBLISHER))
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_1, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_1))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))

        d.addCallback(
            lambda __: self.psclient.publish(SERVICE, OTHER_NODE_ID, [ITEM_2])
        )
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_2, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, OTHER_NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_2))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))

        def clean(res):
            del self.host.plugins["XEP-0060"].node_cache[
                C.PROFILE[0] + "@found@" + SERVICE
            ]
            return res

        d.addCallback(lambda __: self.plugin.deleteAllGroupBlogsComments(C.PROFILE[0]))
        d.addCallback(clean)

        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_1))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))

        d.addCallback(lambda __: self.psclient.items(SERVICE, OTHER_NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_2))
        d.addCallback(lambda items: self.assertEqual(len(items), 0))
        return d

    def test_deleteAllGroupBlogsAndComments(self):
        self._initialise(C.PROFILE[0])
        self.host.profiles[C.PROFILE[0]].roster.addItem(jid.JID(OTHER_PUBLISHER))
        d = self.psclient.publish(SERVICE, NODE_ID, [ITEM_1])
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_1, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_1))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))

        d.addCallback(
            lambda __: self.psclient.publish(SERVICE, OTHER_NODE_ID, [ITEM_2])
        )
        d.addCallback(
            lambda __: self.psclient.publish(
                SERVICE, COMMENTS_NODE_ID_2, [COMMENT_1, COMMENT_2]
            )
        )
        d.addCallback(lambda __: self.psclient.items(SERVICE, OTHER_NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_2))
        d.addCallback(lambda items: self.assertEqual(len(items), 2))

        def clean(res):
            del self.host.plugins["XEP-0060"].node_cache[
                C.PROFILE[0] + "@found@" + SERVICE
            ]
            return res

        d.addCallback(
            lambda __: self.plugin.deleteAllGroupBlogsAndComments(C.PROFILE[0])
        )
        d.addCallback(clean)

        d.addCallback(lambda __: self.psclient.items(SERVICE, NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 0))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_1))
        d.addCallback(lambda items: self.assertEqual(len(items), 0))

        d.addCallback(lambda __: self.psclient.items(SERVICE, OTHER_NODE_ID))
        d.addCallback(lambda items: self.assertEqual(len(items), 1))
        d.addCallback(lambda __: self.psclient.items(SERVICE, COMMENTS_NODE_ID_2))
        d.addCallback(lambda items: self.assertEqual(len(items), 0))
        return d

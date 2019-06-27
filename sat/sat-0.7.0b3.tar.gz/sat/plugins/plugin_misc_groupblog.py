#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for microbloging with roster access
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
from twisted.internet import defer
from sat.core import exceptions
from wokkel import disco, data_form, iwokkel
from zope.interface import implements

try:
    from twisted.words.protocols.xmlstream import XMPPHandler
except ImportError:
    from wokkel.subprotocols import XMPPHandler

NS_PUBSUB = "http://jabber.org/protocol/pubsub"
NS_GROUPBLOG = "http://salut-a-toi.org/protocol/groupblog"
# NS_PUBSUB_EXP = 'http://goffi.org/protocol/pubsub' #for non official features
NS_PUBSUB_EXP = (
    NS_PUBSUB
)  # XXX: we can't use custom namespace as Wokkel's PubSubService use official NS
NS_PUBSUB_GROUPBLOG = NS_PUBSUB_EXP + "#groupblog"
NS_PUBSUB_ITEM_CONFIG = NS_PUBSUB_EXP + "#item-config"


PLUGIN_INFO = {
    C.PI_NAME: "Group blogging through collections",
    C.PI_IMPORT_NAME: "GROUPBLOG",
    C.PI_TYPE: "MISC",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0277"],
    C.PI_MAIN: "GroupBlog",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of microblogging fine permissions"""),
}


class GroupBlog(object):
    """This class use a SàT PubSub Service to manage access on microblog"""

    def __init__(self, host):
        log.info(_("Group blog plugin initialization"))
        self.host = host
        self._p = self.host.plugins["XEP-0060"]
        host.trigger.add("XEP-0277_item2data", self._item2dataTrigger)
        host.trigger.add("XEP-0277_data2entry", self._data2entryTrigger)
        host.trigger.add("XEP-0277_comments", self._commentsTrigger)

    ## plugin management methods ##

    def getHandler(self, client):
        return GroupBlog_handler()

    @defer.inlineCallbacks
    def profileConnected(self, client):
        try:
            yield self.host.checkFeatures(client, (NS_PUBSUB_GROUPBLOG,))
        except exceptions.FeatureNotFound:
            client.server_groupblog_available = False
            log.warning(
                _(
                    u"Server is not able to manage item-access pubsub, we can't use group blog"
                )
            )
        else:
            client.server_groupblog_available = True
            log.info(_(u"Server can manage group blogs"))

    def getFeatures(self, profile):
        try:
            client = self.host.getClient(profile)
        except exceptions.ProfileNotSetError:
            return {}
        try:
            return {"available": C.boolConst(client.server_groupblog_available)}
        except AttributeError:
            if self.host.isConnected(profile):
                log.debug("Profile is not connected, service is not checked yet")
            else:
                log.error("client.server_groupblog_available should be available !")
            return {}

    def _item2dataTrigger(self, item_elt, entry_elt, microblog_data):
        """Parse item to find group permission elements"""
        config_form = data_form.findForm(item_elt, NS_PUBSUB_ITEM_CONFIG)
        if config_form is None:
            return
        access_model = config_form.get(self._p.OPT_ACCESS_MODEL, self._p.ACCESS_OPEN)
        if access_model == self._p.ACCESS_PUBLISHER_ROSTER:
            opt = self._p.OPT_ROSTER_GROUPS_ALLOWED
            microblog_data['groups'] = config_form.fields[opt].values

    def _data2entryTrigger(self, client, mb_data, entry_elt, item_elt):
        """Build fine access permission if needed

        This trigger check if "group*" key are present,
        and create a fine item config to restrict view to these groups
        """
        groups = mb_data.get('groups', [])
        if not groups:
            return
        if not client.server_groupblog_available:
            raise exceptions.CancelError(u"GroupBlog is not available")
        log.debug(u"This entry use group blog")
        form = data_form.Form("submit", formNamespace=NS_PUBSUB_ITEM_CONFIG)
        access = data_form.Field(
            None, self._p.OPT_ACCESS_MODEL, value=self._p.ACCESS_PUBLISHER_ROSTER
        )
        allowed = data_form.Field(None, self._p.OPT_ROSTER_GROUPS_ALLOWED, values=groups)
        form.addField(access)
        form.addField(allowed)
        item_elt.addChild(form.toElement())

    def _commentsTrigger(self, client, mb_data, options):
        """This method is called when a comments node is about to be created

        It changes the access mode to roster if needed, and give the authorized groups
        """
        if "group" in mb_data:
            options[self._p.OPT_ACCESS_MODEL] = self._p.ACCESS_PUBLISHER_ROSTER
            options[self._p.OPT_ROSTER_GROUPS_ALLOWED] = mb_data['groups']

class GroupBlog_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_GROUPBLOG)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

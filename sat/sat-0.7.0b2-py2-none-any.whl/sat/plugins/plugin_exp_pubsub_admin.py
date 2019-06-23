#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin to send pubsub requests with administrator privilege
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
from sat.tools.common import data_format
from twisted.words.protocols.jabber import jid
from wokkel import pubsub
from wokkel import generic

log = getLogger(__name__)

PLUGIN_INFO = {
    C.PI_NAME: u"Pubsub Administrator",
    C.PI_IMPORT_NAME: u"PUBSUB_ADMIN",
    C.PI_TYPE: C.PLUG_TYPE_EXP,
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: u"PubsubAdmin",
    C.PI_HANDLER: u"no",
    C.PI_DESCRIPTION: _(u"""\Implementation of Pubsub Administrator
This allows a pubsub administrator to overwrite completly items, including publisher.
Specially useful when importing a node."""),
}

NS_PUBSUB_ADMIN = u"https://salut-a-toi.org/spec/pubsub_admin:0"


class PubsubAdmin(object):

    def __init__(self, host):
        self.host = host
        host.bridge.addMethod(
            "psAdminItemsSend",
            ".plugin",
            in_sign="ssasss",
            out_sign="as",
            method=self._publish,
            async=True,
        )

    def _publish(self, service, nodeIdentifier, items, extra=None,
                 profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        service = None if not service else jid.JID(service)
        extra = data_format.deserialise(extra)
        items = [generic.parseXml(i.encode('utf-8')) for i in items]
        return self.publish(
            client, service, nodeIdentifier, items, extra
        )

    def _sendCb(self, iq_result):
        publish_elt = iq_result.admin.pubsub.publish
        ids = []
        for item_elt in publish_elt.elements(pubsub.NS_PUBSUB, u'item'):
            ids.append(item_elt[u'id'])
        return ids

    def publish(self, client, service, nodeIdentifier, items, extra=None):
        for item in items:
            if item.name != u'item' or item.uri != pubsub.NS_PUBSUB:
                raise exceptions.DataError(
                    u'Invalid element, a pubsub item is expected: {xml}'.format(
                    xml=item.toXml()))
        iq_elt = client.IQ()
        iq_elt['to'] = service.full() if service else client.jid.userhost()
        admin_elt = iq_elt.addElement((NS_PUBSUB_ADMIN, u'admin'))
        pubsub_elt = admin_elt.addElement((pubsub.NS_PUBSUB, u'pubsub'))
        publish_elt = pubsub_elt.addElement('publish')
        publish_elt[u'node'] = nodeIdentifier
        for item in items:
            publish_elt.addChild(item)
        d = iq_elt.send()
        d.addCallback(self._sendCb)
        return d

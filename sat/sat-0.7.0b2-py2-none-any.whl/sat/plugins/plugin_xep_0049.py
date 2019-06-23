#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for managing xep-0049
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
from wokkel import compat
from twisted.words.xish import domish


PLUGIN_INFO = {
    C.PI_NAME: "XEP-0049 Plugin",
    C.PI_IMPORT_NAME: "XEP-0049",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0049"],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XEP_0049",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Implementation of private XML storage"""),
}


class XEP_0049(object):
    NS_PRIVATE = "jabber:iq:private"

    def __init__(self, host):
        log.info(_("Plugin XEP-0049 initialization"))
        self.host = host

    def privateXMLStore(self, element, profile_key):
        """Store private data
        @param element: domish.Element to store (must have a namespace)
        @param profile_key: %(doc_profile_key)s

        """
        assert isinstance(element, domish.Element)
        client = self.host.getClient(profile_key)
        # XXX: feature announcement in disco#info is not mandatory in XEP-0049, so we have to try to use private XML, and react according to the answer
        iq_elt = compat.IQ(client.xmlstream)
        query_elt = iq_elt.addElement("query", XEP_0049.NS_PRIVATE)
        query_elt.addChild(element)
        return iq_elt.send()

    def privateXMLGet(self, node_name, namespace, profile_key):
        """Store private data
        @param node_name: name of the node to get
        @param namespace: namespace of the node to get
        @param profile_key: %(doc_profile_key)s
        @return (domish.Element): a deferred which fire the stored data

        """
        client = self.host.getClient(profile_key)
        # XXX: see privateXMLStore note about feature checking
        iq_elt = compat.IQ(client.xmlstream, "get")
        query_elt = iq_elt.addElement("query", XEP_0049.NS_PRIVATE)
        query_elt.addElement(node_name, namespace)

        def getCb(answer_iq_elt):
            answer_query_elt = answer_iq_elt.elements(XEP_0049.NS_PRIVATE, "query").next()
            return answer_query_elt.firstChildElement()

        d = iq_elt.send()
        d.addCallback(getCb)
        return d

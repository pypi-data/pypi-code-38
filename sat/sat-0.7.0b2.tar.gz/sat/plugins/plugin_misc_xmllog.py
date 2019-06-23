#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing raw XML log
# Copyright (C) 2011  Jérôme Poisson (goffi@goffi.org)

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
from twisted.words.xish import domish
from functools import partial

PLUGIN_INFO = {
    C.PI_NAME: "Raw XML log Plugin",
    C.PI_IMPORT_NAME: "XmlLog",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XmlLog",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""Send raw XML logs to bridge"""),
}


class XmlLog(object):

    params = """
    <params>
    <general>
    <category name="Debug">
        <param name="Xml log" label="%(label_xmllog)s" value="false" type="bool" />
    </category>
    </general>
    </params>
    """ % {
        "label_xmllog": _("Activate XML log")
    }

    def __init__(self, host):
        log.info(_("Plugin XML Log initialization"))
        self.host = host
        host.memory.updateParams(self.params)
        host.bridge.addSignal(
            "xmlLog", ".plugin", signature="sss"
        )  # args: direction("IN" or "OUT"), xml_data, profile

        host.trigger.add("stream_hooks", self.addHooks)

    def addHooks(self, client, receive_hooks, send_hooks):
        self.do_log = self.host.memory.getParamA("Xml log", "Debug")
        if self.do_log:
            receive_hooks.append(partial(self.onReceive, client=client))
            send_hooks.append(partial(self.onSend, client=client))
            log.info(_(u"XML log activated"))
        return True

    def onReceive(self, element, client):
        self.host.bridge.xmlLog("IN", element.toXml(), client.profile)

    def onSend(self, obj, client):
        if isinstance(obj, basestring):
            log = unicode(obj)
        elif isinstance(obj, domish.Element):
            log = obj.toXml()
        else:
            log.error(_(u"INTERNAL ERROR: Unmanaged XML type"))
        self.host.bridge.xmlLog("OUT", log, client.profile)

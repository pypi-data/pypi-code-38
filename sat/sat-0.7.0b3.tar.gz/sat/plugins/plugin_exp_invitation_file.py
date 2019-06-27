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
from sat.tools.common import data_format
from twisted.words.protocols.jabber import jid

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "File Sharing Invitation",
    C.PI_IMPORT_NAME: "FILE_SHARING_INVITATION",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: ["XEP-0329", u"INVITATION"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "FileSharingInvitation",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"Experimental handling of invitations for file sharing"),
}


class FileSharingInvitation(object):

    def __init__(self, host):
        log.info(_(u"File Sharing Invitation plugin initialization"))
        self.host = host
        ns_fis = host.getNamespace(u"fis")
        host.plugins[u"INVITATION"].registerNamespace(ns_fis, self.onInvitation)
        host.bridge.addMethod(
            "FISInvite",
            ".plugin",
            in_sign="ssssssss",
            out_sign="",
            method=self._sendFileSharingInvitation,
        )

    def _sendFileSharingInvitation(
            self, invitee_jid_s, service_s, repos_type=None, namespace=None, path=None,
            name=None, extra_s=u'', profile_key=C.PROF_KEY_NONE):
        client = self.host.getClient(profile_key)
        invitee_jid = jid.JID(invitee_jid_s)
        service = jid.JID(service_s)
        extra = data_format.deserialise(extra_s)
        return self.host.plugins[u"INVITATION"].sendFileSharingInvitation(
            client, invitee_jid, service, repos_type=repos_type or None,
            namespace=namespace or None, path=path or None, name=name or None,
            extra=extra)

    def onInvitation(self, client, name, extra, service, repos_type, namespace, path):
        if repos_type == u"files":
            type_human = _(u"file sharing")
        elif repos_type == u"photos":
            type_human = _(u"photos album")
        else:
            log.warning(u"Unknown repository type: {repos_type}".format(
                repos_type=repos_type))
            repos_type = u"file"
            type_human = _(u"file sharing")
        log.info(_(
            u'{profile} has received an invitation for a files repository ({type_human}) '
            u'with namespace "{namespace}" at path [{path}]').format(
            profile=client.profile, type_human=type_human, namespace=namespace, path=path)
            )
        return self.host.plugins[u'LIST_INTEREST'].registerFileSharing(
            client, service, repos_type, namespace, path, name, extra)

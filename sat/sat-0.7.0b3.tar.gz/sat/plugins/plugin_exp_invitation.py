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
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.protocols.jabber.xmlstream import XMPPHandler

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Invitation",
    C.PI_IMPORT_NAME: "INVITATION",
    C.PI_TYPE: "EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [u"XEP-0060", u"XEP-0329"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "Invitation",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(u"Experimental handling of invitations"),
}

NS_INVITATION = u"https://salut-a-toi/protocol/invitation:0"
INVITATION = '/message/invitation[@xmlns="{ns_invit}"]'.format(
    ns_invit=NS_INVITATION
)
NS_INVITATION_LIST = NS_INVITATION + u"#list"


class Invitation(object):

    def __init__(self, host):
        log.info(_(u"Invitation plugin initialization"))
        self.host = host
        self._p = self.host.plugins["XEP-0060"]
        # map from namespace of the invitation to callback handling it
        self._ns_cb = {}

    def getHandler(self, client):
        return PubsubInvitationHandler(self)

    def registerNamespace(self, namespace, callback):
        """Register a callback for a namespace

        @param namespace(unicode): namespace handled
        @param callback(callbable): method handling the invitation
            For pubsub invitation, it will be called with following arguments:
                - client
                - name(unicode, None): name of the event
                - extra(dict): extra data
                - service(jid.JID): pubsub service jid
                - node(unicode): pubsub node
                - item_id(unicode, None): pubsub item id
                - item_elt(domish.Element): item of the invitation
            For file sharing invitation, it will be called with following arguments:
                - client
                - name(unicode, None): name of the repository
                - extra(dict): extra data
                - service(jid.JID): service jid of the file repository
                - repos_type(unicode): type of the repository, can be:
                    - files: generic file sharing
                    - photos: photos album
                - namespace(unicode, None): namespace of the repository
                - path(unicode, None): path of the repository
        @raise exceptions.ConflictError: this namespace is already registered
        """
        if namespace in self._ns_cb:
            raise exceptions.ConflictError(
                u"invitation namespace {namespace} is already register with {callback}"
                .format(namespace=namespace, callback=self._ns_cb[namespace]))
        self._ns_cb[namespace] = callback

    def _generateBaseInvitation(self, client, invitee_jid, name, extra):
        """Generate common mess_data end invitation_elt

        @param invitee_jid(jid.JID): entitee to send invitation to
        @param name(unicode, None): name of the shared repository
        @param extra(dict, None): extra data, where key can be:
            - thumb_url: URL of a thumbnail
        @return (tuple[dict, domish.Element): mess_data and invitation_elt
        """
        mess_data = {
            "from": client.jid,
            "to": invitee_jid,
            "uid": "",
            "message": {},
            "type": C.MESS_TYPE_CHAT,
            "subject": {},
            "extra": {},
        }
        client.generateMessageXML(mess_data)
        invitation_elt = mess_data["xml"].addElement("invitation", NS_INVITATION)
        if name is not None:
            invitation_elt[u"name"] = name
        thumb_url = extra.get(u'thumb_url')
        if thumb_url:
            if not thumb_url.startswith(u'http'):
                log.warning(
                    u"only http URLs are allowed for thumbnails, got {url}, ignoring"
                    .format(url=thumb_url))
            else:
                invitation_elt[u'thumb_url'] = thumb_url
        return mess_data, invitation_elt

    def sendPubsubInvitation(self, client, invitee_jid, service, node,
                             item_id, name, extra):
        """Send an pubsub invitation in a <message> stanza

        @param invitee_jid(jid.JID): entitee to send invitation to
        @param service(jid.JID): pubsub service
        @param node(unicode): pubsub node
        @param item_id(unicode): pubsub id
        @param name(unicode, None): see [_generateBaseInvitation]
        @param extra(dict, None): see [_generateBaseInvitation]
        """
        if extra is None:
            extra = {}
        mess_data, invitation_elt = self._generateBaseInvitation(
            client, invitee_jid, name, extra)
        pubsub_elt = invitation_elt.addElement(u"pubsub")
        pubsub_elt[u"service"] = service.full()
        pubsub_elt[u"node"] = node
        pubsub_elt[u"item"] = item_id
        return client.send(mess_data[u"xml"])

    def sendFileSharingInvitation(self, client, invitee_jid, service, repos_type=None,
                                  namespace=None, path=None, name=None, extra=None):
        """Send a file sharing invitation in a <message> stanza

        @param invitee_jid(jid.JID): entitee to send invitation to
        @param service(jid.JID): file sharing service
        @param repos_type(unicode, None): type of files repository, can be:
            - None, "files": files sharing
            - "photos": photos album
        @param namespace(unicode, None): namespace of the shared repository
        @param path(unicode, None): path of the shared repository
        @param name(unicode, None): see [_generateBaseInvitation]
        @param extra(dict, None): see [_generateBaseInvitation]
        """
        if extra is None:
            extra = {}
        mess_data, invitation_elt = self._generateBaseInvitation(
            client, invitee_jid, name, extra)
        file_sharing_elt = invitation_elt.addElement(u"file_sharing")
        file_sharing_elt[u"service"] = service.full()
        if repos_type is not None:
            if repos_type not in (u"files", "photos"):
                msg = u"unknown repository type: {repos_type}".format(
                    repos_type=repos_type)
                log.warning(msg)
                raise exceptions.DateError(msg)
            file_sharing_elt[u"type"] = repos_type
        if namespace is not None:
            file_sharing_elt[u"namespace"] = namespace
        if path is not None:
            file_sharing_elt[u"path"] = path
        return client.send(mess_data[u"xml"])

    @defer.inlineCallbacks
    def _parsePubsubElt(self, client, pubsub_elt):
        try:
            service = jid.JID(pubsub_elt["service"])
            node = pubsub_elt["node"]
            item_id = pubsub_elt.getAttribute("item")
        except (RuntimeError, KeyError):
            log.warning(_(u"Bad invitation, ignoring"))
            raise exceptions.DataError

        try:
            items, metadata = yield self._p.getItems(client, service, node,
                                                     item_ids=[item_id])
        except Exception as e:
            log.warning(_(u"Can't get item linked with invitation: {reason}").format(
                        reason=e))
        try:
            item_elt = items[0]
        except IndexError:
            log.warning(_(u"Invitation was linking to a non existing item"))
            raise exceptions.DataError

        try:
            namespace = item_elt.firstChildElement().uri
        except Exception as e:
            log.warning(_(u"Can't retrieve namespace of invitation: {reason}").format(
                reason = e))
            raise exceptions.DataError

        args = [service, node, item_id, item_elt]
        defer.returnValue((namespace, args))

    def _parseFileSharingElt(self, client, file_sharing_elt):
        try:
            service = jid.JID(file_sharing_elt["service"])
        except (RuntimeError, KeyError):
            log.warning(_(u"Bad invitation, ignoring"))
            raise exceptions.DataError
        repos_type = file_sharing_elt.getAttribute(u"type", u"files")
        namespace = file_sharing_elt.getAttribute(u"namespace")
        path = file_sharing_elt.getAttribute(u"path")
        args = [service, repos_type, namespace, path]
        ns_fis = self.host.getNamespace(u"fis")
        return ns_fis, args

    @defer.inlineCallbacks
    def onInvitation(self, message_elt, client):
        log.debug(u"invitation received [{profile}]".format(profile=client.profile))
        invitation_elt = message_elt.invitation

        name = invitation_elt.getAttribute(u"name")
        extra = {}
        if invitation_elt.hasAttribute(u"thumb_url"):
            extra[u'thumb_url'] = invitation_elt[u'thumb_url']

        for elt in invitation_elt.elements():
            if elt.uri != NS_INVITATION:
                log.warning(u"unexpected element: {xml}".format(xml=elt.toXml()))
                continue
            if elt.name == u"pubsub":
                method = self._parsePubsubElt
            elif elt.name == u"file_sharing":
                method = self._parseFileSharingElt
            else:
                log.warning(u"not implemented invitation element: {xml}".format(
                    xml = elt.toXml()))
                continue
            try:
                namespace, args = yield method(client, elt)
            except exceptions.DataError:
                log.warning(u"Can't parse invitation element: {xml}".format(
                            xml = elt.toXml()))
                continue

            try:
                cb = self._ns_cb[namespace]
            except KeyError:
                log.warning(_(
                    u'No handler for namespace "{namespace}", invitation ignored')
                    .format(namespace=namespace))
            else:
                cb(client, name, extra, *args)


class PubsubInvitationHandler(XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent

    def connectionInitialized(self):
        self.xmlstream.addObserver(
            INVITATION, self.plugin_parent.onInvitation, client=self.parent
        )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [
            disco.DiscoFeature(NS_INVITATION),
        ]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

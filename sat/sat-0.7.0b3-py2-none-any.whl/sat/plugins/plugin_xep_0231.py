#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Bit of Binary handling (XEP-0231)
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
from sat.core import exceptions
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.tools import xml_tools
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.python import failure
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as jabber_error
from twisted.internet import defer
from functools import partial
import base64
import time


PLUGIN_INFO = {
    C.PI_NAME: "Bits of Binary",
    C.PI_IMPORT_NAME: "XEP-0231",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0231"],
    C.PI_MAIN: "XEP_0231",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(
        """Implementation of bits of binary (used for small images/files)"""
    ),
}

NS_BOB = u"urn:xmpp:bob"
IQ_BOB_REQUEST = C.IQ_GET + '/data[@xmlns="' + NS_BOB + '"]'


class XEP_0231(object):
    def __init__(self, host):
        log.info(_(u"plugin Bits of Binary initialization"))
        self.host = host
        host.registerNamespace("bob", NS_BOB)
        host.trigger.add("xhtml_post_treat", self.XHTMLTrigger)
        host.bridge.addMethod(
            "bobGetFile",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=self._getFile,
            async=True,
        )

    def dumpData(self, cache, data_elt, cid):
        """save file encoded in data_elt to cache

        @param cache(memory.cache.Cache): cache to use to store the data
        @param data_elt(domish.Element): <data> as in XEP-0231
        @param cid(unicode): content-id
        @return(unicode): full path to dumped file
        """
        #  FIXME: is it needed to use a separate thread?
        #        probably not with the little data expected with BoB
        try:
            max_age = int(data_elt["max-age"])
            if max_age < 0:
                raise ValueError
        except (KeyError, ValueError):
            log.warning(u"invalid max-age found")
            max_age = None

        with cache.cacheData(
            PLUGIN_INFO[C.PI_IMPORT_NAME], cid, data_elt.getAttribute("type"), max_age
        ) as f:

            file_path = f.name
            f.write(base64.b64decode(str(data_elt)))

        return file_path

    def getHandler(self, client):
        return XEP_0231_handler(self)

    def _requestCb(self, iq_elt, cache, cid):
        for data_elt in iq_elt.elements(NS_BOB, u"data"):
            if data_elt.getAttribute("cid") == cid:
                file_path = self.dumpData(cache, data_elt, cid)
                return file_path

        log.warning(
            u"invalid data stanza received, requested cid was not found:\n{iq_elt}\nrequested cid: {cid}".format(
                iq_elt=iq_elt, cid=cid
            )
        )
        raise failure.Failure(exceptions.DataError("missing data"))

    def _requestEb(self, failure_):
        """Log the error and continue errback chain"""
        log.warning(u"Can't get requested data:\n{reason}".format(reason=failure_))
        return failure_

    def requestData(self, client, to_jid, cid, cache=None):
        """Request data if we don't have it in cache

        @param to_jid(jid.JID): jid to request the data to
        @param cid(unicode): content id
        @param cache(memory.cache.Cache, None): cache to use
            client.cache will be used if None
        @return D(unicode): path to file with data
        """
        if cache is None:
            cache = client.cache
        iq_elt = client.IQ("get")
        iq_elt["to"] = to_jid.full()
        data_elt = iq_elt.addElement((NS_BOB, "data"))
        data_elt["cid"] = cid
        d = iq_elt.send()
        d.addCallback(self._requestCb, cache, cid)
        d.addErrback(self._requestEb)
        return d

    def _setImgEltSrc(self, path, img_elt):
        img_elt[u"src"] = u"file://{}".format(path)

    def XHTMLTrigger(self, client, message_elt, body_elt, lang, treat_d):
        for img_elt in xml_tools.findAll(body_elt, C.NS_XHTML, u"img"):
            source = img_elt.getAttribute(u"src", "")
            if source.startswith(u"cid:"):
                cid = source[4:]
                file_path = client.cache.getFilePath(cid)
                if file_path is not None:
                    #  image is in cache, we change the url
                    img_elt[u"src"] = u"file://{}".format(file_path)
                    continue
                else:
                    # image is not in cache, is it given locally?
                    for data_elt in message_elt.elements(NS_BOB, u"data"):
                        if data_elt.getAttribute("cid") == cid:
                            file_path = self.dumpData(client.cache, data_elt, cid)
                            img_elt[u"src"] = u"file://{}".format(file_path)
                            break
                    else:
                        # cid not found locally, we need to request it
                        # so we use the deferred
                        d = self.requestData(client, jid.JID(message_elt["from"]), cid)
                        d.addCallback(partial(self._setImgEltSrc, img_elt=img_elt))
                        treat_d.addCallback(lambda __: d)

    def onComponentRequest(self, iq_elt, client):
        """cache data is retrieve from common cache for components"""
        # FIXME: this is a security/privacy issue as no access check is done
        #        but this is mitigated by the fact that the cid must be known.
        #        An access check should be implemented though.

        iq_elt.handled = True
        data_elt = next(iq_elt.elements(NS_BOB, "data"))
        try:
            cid = data_elt[u"cid"]
        except KeyError:
            error_elt = jabber_error.StanzaError("not-acceptable").toResponse(iq_elt)
            client.send(error_elt)
            return

        metadata = self.host.common_cache.getMetadata(cid)
        if metadata is None:
            error_elt = jabber_error.StanzaError("item-not-found").toResponse(iq_elt)
            client.send(error_elt)
            return

        with open(metadata["path"]) as f:
            data = f.read()

        result_elt = xmlstream.toResponse(iq_elt, "result")
        data_elt = result_elt.addElement((NS_BOB, "data"), content=data.encode("base64"))
        data_elt[u"cid"] = cid
        data_elt[u"type"] = metadata[u"mime_type"]
        data_elt[u"max-age"] = unicode(int(max(0, metadata["eol"] - time.time())))
        client.send(result_elt)

    def _getFile(self, peer_jid_s, cid, profile):
        peer_jid = jid.JID(peer_jid_s)
        assert cid
        client = self.host.getClient(profile)
        return self.getFile(client, peer_jid, cid)

    def getFile(self, client, peer_jid, cid, parent_elt=None):
        """Retrieve a file from it's content-id

        @param peer_jid(jid.JID): jid of the entity offering the data
        @param cid(unicode): content-id of file data
        @param parent_elt(domish.Element, None): if file is not in cache,
            data will be looked after in children of this elements.
            None to ignore
        @return D(unicode): path to cached data
        """
        file_path = client.cache.getFilePath(cid)
        if file_path is not None:
            #  file is in cache
            return defer.succeed(file_path)
        else:
            # file not in cache, is it given locally?
            if parent_elt is not None:
                for data_elt in parent_elt.elements(NS_BOB, u"data"):
                    if data_elt.getAttribute("cid") == cid:
                        return defer.succeed(self.dumpData(client.cache, data_elt, cid))

            # cid not found locally, we need to request it
            # so we use the deferred
            return self.requestData(client, peer_jid, cid)


class XEP_0231_handler(xmlstream.XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        if self.parent.is_component:
            self.xmlstream.addObserver(
                IQ_BOB_REQUEST, self.plugin_parent.onComponentRequest, client=self.parent
            )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_BOB)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

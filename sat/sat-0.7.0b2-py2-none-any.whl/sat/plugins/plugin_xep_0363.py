#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for HTTP File Upload (XEP-0363)
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
from sat.core import exceptions
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.internet import reactor
from twisted.internet import defer
from twisted.internet import ssl
from twisted.internet.interfaces import IOpenSSLClientConnectionCreator
from twisted.web import client as http_client
from twisted.web import http_headers
from twisted.web import iweb
from twisted.python import failure
from collections import namedtuple
from zope.interface import implementer
from OpenSSL import SSL
import os.path
import mimetypes


PLUGIN_INFO = {
    C.PI_NAME: "HTTP File Upload",
    C.PI_IMPORT_NAME: "XEP-0363",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0363"],
    C.PI_DEPENDENCIES: ["FILE", "UPLOAD"],
    C.PI_MAIN: "XEP_0363",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(u"""Implementation of HTTP File Upload"""),
}

NS_HTTP_UPLOAD = "urn:xmpp:http:upload:0"
ALLOWED_HEADERS = ('authorization', 'cookie', 'expires')


Slot = namedtuple("Slot", ["put", "get", "headers"])


@implementer(IOpenSSLClientConnectionCreator)
class NoCheckConnectionCreator(object):
    def __init__(self, hostname, ctx):
        self._ctx = ctx

    def clientConnectionForTLS(self, tlsProtocol):
        context = self._ctx
        connection = SSL.Connection(context, None)
        connection.set_app_data(tlsProtocol)
        return connection


@implementer(iweb.IPolicyForHTTPS)
class NoCheckContextFactory(ssl.ClientContextFactory):
    """Context factory which doesn't do TLS certificate check

    /!\\ it's obvisously a security flaw to use this class,
    and it should be used only with explicite agreement from the end used
    """

    def creatorForNetloc(self, hostname, port):
        log.warning(
            u"TLS check disabled for {host} on port {port}".format(
                host=hostname, port=port
            )
        )
        certificateOptions = ssl.CertificateOptions(trustRoot=None)
        return NoCheckConnectionCreator(hostname, certificateOptions.getContext())


class XEP_0363(object):
    def __init__(self, host):
        log.info(_("plugin HTTP File Upload initialization"))
        self.host = host
        host.bridge.addMethod(
            "fileHTTPUpload",
            ".plugin",
            in_sign="sssbs",
            out_sign="",
            method=self._fileHTTPUpload,
        )
        host.bridge.addMethod(
            "fileHTTPUploadGetSlot",
            ".plugin",
            in_sign="sisss",
            out_sign="(ss)",
            method=self._getSlot,
            async=True,
        )
        host.plugins["UPLOAD"].register(
            u"HTTP Upload", self.getHTTPUploadEntity, self.fileHTTPUpload
        )

    def getHandler(self, client):
        return XEP_0363_handler()

    @defer.inlineCallbacks
    def getHTTPUploadEntity(self, upload_jid=None, profile=C.PROF_KEY_NONE):
        """Get HTTP upload capable entity

         upload_jid is checked, then its components
         @param upload_jid(None, jid.JID): entity to check
         @return(D(jid.JID)): first HTTP upload capable entity
         @raise exceptions.NotFound: no entity found
         """
        client = self.host.getClient(profile)
        try:
            entity = client.http_upload_service
        except AttributeError:
            found_entities = yield self.host.findFeaturesSet(client, (NS_HTTP_UPLOAD,))
            try:
                entity = client.http_upload_service = iter(found_entities).next()
            except StopIteration:
                entity = client.http_upload_service = None

        if entity is None:
            raise failure.Failure(exceptions.NotFound(u"No HTTP upload entity found"))

        defer.returnValue(entity)

    def _fileHTTPUpload(self, filepath, filename="", upload_jid="",
                        ignore_tls_errors=False, profile=C.PROF_KEY_NONE):
        assert os.path.isabs(filepath) and os.path.isfile(filepath)
        progress_id_d, __ = self.fileHTTPUpload(
            filepath,
            filename or None,
            jid.JID(upload_jid) if upload_jid else None,
            {"ignore_tls_errors": ignore_tls_errors},
            profile,
        )
        return progress_id_d

    def fileHTTPUpload(self, filepath, filename=None, upload_jid=None, options=None,
                       profile=C.PROF_KEY_NONE):
        """Upload a file through HTTP

        @param filepath(str): absolute path of the file
        @param filename(None, unicode): name to use for the upload
            None to use basename of the path
        @param upload_jid(jid.JID, None): upload capable entity jid,
            or None to use autodetected, if possible
        @param options(dict): options where key can be:
            - ignore_tls_errors(bool): if True, SSL certificate will not be checked
        @param profile: %(doc_profile)s
        @return (D(tuple[D(unicode), D(unicode)])): progress id and Deferred which fire
            download URL
        """
        if options is None:
            options = {}
        ignore_tls_errors = options.get("ignore_tls_errors", False)
        client = self.host.getClient(profile)
        filename = filename or os.path.basename(filepath)
        size = os.path.getsize(filepath)
        progress_id_d = defer.Deferred()
        download_d = defer.Deferred()
        d = self.getSlot(client, filename, size, upload_jid=upload_jid)
        d.addCallbacks(
            self._getSlotCb,
            self._getSlotEb,
            (client, progress_id_d, download_d, filepath, size, ignore_tls_errors),
            None,
            (client, progress_id_d, download_d),
        )
        return progress_id_d, download_d

    def _getSlotEb(self, fail, client, progress_id_d, download_d):
        """an error happened while trying to get slot"""
        log.warning(u"Can't get upload slot: {reason}".format(reason=fail.value))
        progress_id_d.errback(fail)
        download_d.errback(fail)

    def _getSlotCb(self, slot, client, progress_id_d, download_d, path, size,
                   ignore_tls_errors=False):
        """Called when slot is received, try to do the upload

        @param slot(Slot): slot instance with the get and put urls
        @param progress_id_d(defer.Deferred): Deferred to call when progress_id is known
        @param progress_id_d(defer.Deferred): Deferred to call with URL when upload is
            done
        @param path(str): path to the file to upload
        @param size(int): size of the file to upload
        @param ignore_tls_errors(bool): ignore TLS certificate is True
        @return (tuple
        """
        log.debug(u"Got upload slot: {}".format(slot))
        sat_file = self.host.plugins["FILE"].File(
            self.host, client, path, size=size, auto_end_signals=False
        )
        progress_id_d.callback(sat_file.uid)
        file_producer = http_client.FileBodyProducer(sat_file)
        if ignore_tls_errors:
            agent = http_client.Agent(reactor, NoCheckContextFactory())
        else:
            agent = http_client.Agent(reactor)

        headers = {"User-Agent": [C.APP_NAME.encode("utf-8")]}
        for name, value in slot.headers:
            name = name.encode('utf-8')
            value = value.encode('utf-8')
            headers[name] = value

        d = agent.request(
            "PUT",
            slot.put.encode("utf-8"),
            http_headers.Headers(headers),
            file_producer,
        )
        d.addCallbacks(
            self._uploadCb,
            self._uploadEb,
            (sat_file, slot, download_d),
            None,
            (sat_file, download_d),
        )
        return d

    def _uploadCb(self, __, sat_file, slot, download_d):
        """Called once file is successfully uploaded

        @param sat_file(SatFile): file used for the upload
            should be closed, be is needed to send the progressFinished signal
        @param slot(Slot): put/get urls
        """
        log.info(u"HTTP upload finished")
        sat_file.progressFinished({"url": slot.get})
        download_d.callback(slot.get)

    def _uploadEb(self, fail, sat_file, download_d):
        """Called on unsuccessful upload

        @param sat_file(SatFile): file used for the upload
            should be closed, be is needed to send the progressError signal
        """
        download_d.errback(fail)
        try:
            wrapped_fail = fail.value.reasons[0]
        except (AttributeError, IndexError) as e:
            log.warning(_(u"upload failed: {reason}").format(reason=e))
            sat_file.progressError(unicode(fail))
            raise fail
        else:
            if wrapped_fail.check(SSL.Error):
                msg = u"TLS validation error, can't connect to HTTPS server"
            else:
                msg = u"can't upload file"
            log.warning(msg + ": " + unicode(wrapped_fail.value))
            sat_file.progressError(msg)

    def _gotSlot(self, iq_elt, client):
        """Slot have been received

        This method convert the iq_elt result to a Slot instance
        @param iq_elt(domish.Element): <IQ/> result as specified in XEP-0363
        """
        try:
            slot_elt = iq_elt.elements(NS_HTTP_UPLOAD, "slot").next()
            put_elt = slot_elt.elements(NS_HTTP_UPLOAD, "put").next()
            put_url = put_elt['url']
            get_elt = slot_elt.elements(NS_HTTP_UPLOAD, "get").next()
            get_url = get_elt['url']
        except (StopIteration, KeyError):
            raise exceptions.DataError(u"Incorrect stanza received from server")
        headers = []
        for header_elt in put_elt.elements(NS_HTTP_UPLOAD, "header"):
            try:
                name = header_elt["name"]
                value = unicode(header_elt)
            except KeyError:
                log.warning(_(u"Invalid header element: {xml}").format(
                    iq_elt.toXml()))
                continue
            name = name.replace('\n', '')
            value = value.replace('\n', '')
            if name.lower() not in ALLOWED_HEADERS:
                log.warning(_(u'Ignoring unauthorised header "{name}": {xml}')
                    .format(name=name, xml = iq_elt.toXml()))
                continue
            headers.append((name, value))

        slot = Slot(put=put_url, get=get_url, headers=tuple(headers))
        return slot

    def _getSlot(self, filename, size, content_type, upload_jid,
                 profile_key=C.PROF_KEY_NONE):
        """Get an upload slot

        This method can be used when uploading is done by the frontend
        @param filename(unicode): name of the file to upload
        @param size(int): size of the file (must be non null)
        @param upload_jid(jid.JID(), None, ''): HTTP upload capable entity
        @param content_type(unicode, None): MIME type of the content
            empty string or None to guess automatically
        """
        filename = filename.replace("/", "_")
        client = self.host.getClient(profile_key)
        return self.getSlot(
            client, filename, size, content_type or None, upload_jid or None
        )

    def getSlot(self, client, filename, size, content_type=None, upload_jid=None):
        """Get a slot (i.e. download/upload links)

        @param filename(unicode): name to use for the upload
        @param size(int): size of the file to upload (must be >0)
        @param content_type(None, unicode): MIME type of the content
            None to autodetect
        @param upload_jid(jid.JID, None): HTTP upload capable upload_jid
            or None to use the server component (if any)
        @param client: %(doc_client)s
        @return (Slot): the upload (put) and download (get) URLs
        @raise exceptions.NotFound: no HTTP upload capable upload_jid has been found
        """
        assert filename and size
        if content_type is None:
            # TODO: manage python magic for file guessing (in a dedicated plugin ?)
            content_type = mimetypes.guess_type(filename, strict=False)[0]

        if upload_jid is None:
            try:
                upload_jid = client.http_upload_service
            except AttributeError:
                d = self.getHTTPUploadEntity(profile=client.profile)
                d.addCallback(
                    lambda found_entity: self.getSlot(
                        client, filename, size, content_type, found_entity
                    )
                )
                return d
            else:
                if upload_jid is None:
                    raise failure.Failure(
                        exceptions.NotFound(u"No HTTP upload entity found")
                    )

        iq_elt = client.IQ("get")
        iq_elt["to"] = upload_jid.full()
        request_elt = iq_elt.addElement((NS_HTTP_UPLOAD, "request"))
        request_elt["filename"] = filename
        request_elt["size"] = unicode(size)
        if content_type is not None:
            request_elt["content-type"] = content_type

        d = iq_elt.send()
        d.addCallback(self._gotSlot, client)

        return d


class XEP_0363_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_HTTP_UPLOAD)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

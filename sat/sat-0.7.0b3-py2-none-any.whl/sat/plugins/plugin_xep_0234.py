#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Jingle File Transfer (XEP-0234)
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
from sat.tools import utils
from sat.tools import stream
from sat.tools.common import date_utils
import os.path
from twisted.words.xish import domish
from twisted.words.protocols.jabber import jid
from twisted.python import failure
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.internet import defer
from twisted.internet import reactor
from twisted.internet import error as internet_error
from collections import namedtuple
from sat.tools.common import regex
import mimetypes


NS_JINGLE_FT = "urn:xmpp:jingle:apps:file-transfer:5"

PLUGIN_INFO = {
    C.PI_NAME: "Jingle File Transfer",
    C.PI_IMPORT_NAME: "XEP-0234",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0234"],
    C.PI_DEPENDENCIES: ["XEP-0166", "XEP-0300", "FILE"],
    C.PI_MAIN: "XEP_0234",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Jingle File Transfer"""),
}

EXTRA_ALLOWED = {u"path", u"namespace", u"file_desc", u"file_hash"}
Range = namedtuple("Range", ("offset", "length"))


class XEP_0234(object):
    # TODO: assure everything is closed when file is sent or session terminate is received
    # TODO: call self._f.unregister when unloading order will be managing (i.e. when dependencies will be unloaded at the end)
    Range = Range  # we copy the class here, so it can be used by other plugins

    def __init__(self, host):
        log.info(_("plugin Jingle File Transfer initialization"))
        self.host = host
        host.registerNamespace("jingle-ft", NS_JINGLE_FT)
        self._j = host.plugins["XEP-0166"]  # shortcut to access jingle
        self._j.registerApplication(NS_JINGLE_FT, self)
        self._f = host.plugins["FILE"]
        self._f.register(
            NS_JINGLE_FT, self.fileJingleSend, priority=10000, method_name=u"Jingle"
        )
        self._hash = self.host.plugins["XEP-0300"]
        host.bridge.addMethod(
            "fileJingleSend",
            ".plugin",
            in_sign="ssssa{ss}s",
            out_sign="",
            method=self._fileJingleSend,
            async=True,
        )
        host.bridge.addMethod(
            "fileJingleRequest",
            ".plugin",
            in_sign="sssssa{ss}s",
            out_sign="s",
            method=self._fileJingleRequest,
            async=True,
        )

    def getHandler(self, client):
        return XEP_0234_handler()

    def getProgressId(self, session, content_name):
        """Return a unique progress ID

        @param session(dict): jingle session
        @param content_name(unicode): name of the content
        @return (unicode): unique progress id
        """
        return u"{}_{}".format(session["id"], content_name)

    # generic methods

    def buildFileElement(self, name, file_hash=None, hash_algo=None, size=None,
        mime_type=None, desc=None, modified=None, transfer_range=None, path=None,
        namespace=None, file_elt=None, **kwargs):
        """Generate a <file> element with available metadata

        @param file_hash(unicode, None): hash of the file
            empty string to set <hash-used/> element
        @param hash_algo(unicode, None): hash algorithm used
            if file_hash is None and hash_algo is set, a <hash-used/> element will be generated
        @param transfer_range(Range, None): where transfer must start/stop
        @param modified(int, unicode, None): date of last modification
            0 to use current date
            int to use an unix timestamp
            else must be an unicode string which will be used as it (it must be an XMPP time)
        @param file_elt(domish.Element, None): element to use
            None to create a new one
        @param **kwargs: data for plugin extension (ignored by default)
        @return (domish.Element): generated element
        @trigger XEP-0234_buildFileElement(file_elt, extra_args): can be used to extend elements to add
        """
        if file_elt is None:
            file_elt = domish.Element((NS_JINGLE_FT, u"file"))
        for name, value in (
            (u"name", name),
            (u"size", size),
            ("media-type", mime_type),
            (u"desc", desc),
            (u"path", path),
            (u"namespace", namespace),
        ):
            if value is not None:
                file_elt.addElement(name, content=unicode(value))

        if modified is not None:
            if isinstance(modified, int):
                file_elt.addElement(u"date", utils.xmpp_date(modified or None))
            else:
                file_elt.addElement(u"date", modified)
        elif "created" in kwargs:
            file_elt.addElement(u"date", utils.xmpp_date(kwargs.pop("created")))

        range_elt = file_elt.addElement(u"range")
        if transfer_range is not None:
            if transfer_range.offset is not None:
                range_elt[u"offset"] = transfer_range.offset
            if transfer_range.length is not None:
                range_elt[u"length"] = transfer_range.length
        if file_hash is not None:
            if not file_hash:
                file_elt.addChild(self._hash.buildHashUsedElt())
            else:
                file_elt.addChild(self._hash.buildHashElt(file_hash, hash_algo))
        elif hash_algo is not None:
            file_elt.addChild(self._hash.buildHashUsedElt(hash_algo))
        self.host.trigger.point(u"XEP-0234_buildFileElement", file_elt, extra_args=kwargs)
        if kwargs:
            for kw in kwargs:
                log.debug("ignored keyword: {}".format(kw))
        return file_elt

    def buildFileElementFromDict(self, file_data, **kwargs):
        """like buildFileElement but get values from a file_data dict

        @param file_data(dict): metadata to use
        @param **kwargs: data to override
        """
        if kwargs:
            file_data = file_data.copy()
            file_data.update(kwargs)
        return self.buildFileElement(**file_data)

    def parseFileElement(
        self,
        file_elt,
        file_data=None,
        given=False,
        parent_elt=None,
        keep_empty_range=False,
    ):
        """Parse a <file> element and file dictionary accordingly

        @param file_data(dict, None): dict where the data will be set
            following keys will be set (and overwritten if they already exist):
                name, file_hash, hash_algo, size, mime_type, desc, path, namespace, range
            if None, a new dict is created
        @param given(bool): if True, prefix hash key with "given_"
        @param parent_elt(domish.Element, None): parent of the file element
            if set, file_elt must not be set
        @param keep_empty_range(bool): if True, keep empty range (i.e. range when offset and length are None)
            empty range are useful to know if a peer_jid can handle range
        @return (dict): file_data
        @trigger XEP-0234_parseFileElement(file_elt, file_data): can be used to parse new elements
        @raise exceptions.NotFound: there is not <file> element in parent_elt
        @raise exceptions.DataError: if file_elt uri is not NS_JINGLE_FT
        """
        if parent_elt is not None:
            if file_elt is not None:
                raise exceptions.InternalError(
                    u"file_elt must be None if parent_elt is set"
                )
            try:
                file_elt = next(parent_elt.elements(NS_JINGLE_FT, u"file"))
            except StopIteration:
                raise exceptions.NotFound()
        else:
            if not file_elt or file_elt.uri != NS_JINGLE_FT:
                raise exceptions.DataError(
                    u"invalid <file> element: {stanza}".format(stanza=file_elt.toXml())
                )

        if file_data is None:
            file_data = {}

        for name in (u"name", u"desc", u"path", u"namespace"):
            try:
                file_data[name] = unicode(next(file_elt.elements(NS_JINGLE_FT, name)))
            except StopIteration:
                pass

        name = file_data.get(u"name")
        if name == u"..":
            # we don't want to go to parent dir when joining to a path
            name = u"--"
            file_data[u"name"] = name
        elif name is not None and u"/" in name or u"\\" in name:
            file_data[u"name"] = regex.pathEscape(name)

        try:
            file_data[u"mime_type"] = unicode(
                next(file_elt.elements(NS_JINGLE_FT, u"media-type"))
            )
        except StopIteration:
            pass

        try:
            file_data[u"size"] = int(
                unicode(next(file_elt.elements(NS_JINGLE_FT, u"size")))
            )
        except StopIteration:
            pass

        try:
            file_data[u"modified"] = date_utils.date_parse(
                next(file_elt.elements(NS_JINGLE_FT, u"date"))
            )
        except StopIteration:
            pass

        try:
            range_elt = file_elt.elements(NS_JINGLE_FT, u"range").next()
        except StopIteration:
            pass
        else:
            offset = range_elt.getAttribute("offset")
            length = range_elt.getAttribute("length")
            if offset or length or keep_empty_range:
                file_data[u"transfer_range"] = Range(offset=offset, length=length)

        prefix = u"given_" if given else u""
        hash_algo_key, hash_key = u"hash_algo", prefix + u"file_hash"
        try:
            file_data[hash_algo_key], file_data[hash_key] = self._hash.parseHashElt(
                file_elt
            )
        except exceptions.NotFound:
            pass

        self.host.trigger.point(u"XEP-0234_parseFileElement", file_elt, file_data)

        return file_data

    # bridge methods

    def _fileJingleSend(
        self,
        peer_jid,
        filepath,
        name="",
        file_desc="",
        extra=None,
        profile=C.PROF_KEY_NONE,
    ):
        client = self.host.getClient(profile)
        return self.fileJingleSend(
            client,
            jid.JID(peer_jid),
            filepath,
            name or None,
            file_desc or None,
            extra or None,
        )

    @defer.inlineCallbacks
    def fileJingleSend(
        self, client, peer_jid, filepath, name, file_desc=None, extra=None
    ):
        """Send a file using jingle file transfer

        @param peer_jid(jid.JID): destinee jid
        @param filepath(str): absolute path of the file
        @param name(unicode, None): name of the file
        @param file_desc(unicode, None): description of the file
        @return (D(unicode)): progress id
        """
        progress_id_d = defer.Deferred()
        if extra is None:
            extra = {}
        if file_desc is not None:
            extra["file_desc"] = file_desc
        yield self._j.initiate(
            client,
            peer_jid,
            [
                {
                    "app_ns": NS_JINGLE_FT,
                    "senders": self._j.ROLE_INITIATOR,
                    "app_kwargs": {
                        "filepath": filepath,
                        "name": name,
                        "extra": extra,
                        "progress_id_d": progress_id_d,
                    },
                }
            ],
        )
        progress_id = yield progress_id_d
        defer.returnValue(progress_id)

    def _fileJingleRequest(
        self,
        peer_jid,
        filepath,
        name="",
        file_hash="",
        hash_algo="",
        extra=None,
        profile=C.PROF_KEY_NONE,
    ):
        client = self.host.getClient(profile)
        return self.fileJingleRequest(
            client,
            jid.JID(peer_jid),
            filepath,
            name or None,
            file_hash or None,
            hash_algo or None,
            extra or None,
        )

    @defer.inlineCallbacks
    def fileJingleRequest(
        self,
        client,
        peer_jid,
        filepath,
        name=None,
        file_hash=None,
        hash_algo=None,
        extra=None,
    ):
        """Request a file using jingle file transfer

        @param peer_jid(jid.JID): destinee jid
        @param filepath(str): absolute path where the file will be downloaded
        @param name(unicode, None): name of the file
        @param file_hash(unicode, None): hash of the file
        @return (D(unicode)): progress id
        """
        progress_id_d = defer.Deferred()
        if extra is None:
            extra = {}
        if file_hash is not None:
            if hash_algo is None:
                raise ValueError(_(u"hash_algo must be set if file_hash is set"))
            extra["file_hash"] = file_hash
            extra["hash_algo"] = hash_algo
        else:
            if hash_algo is not None:
                raise ValueError(_(u"file_hash must be set if hash_algo is set"))
        yield self._j.initiate(
            client,
            peer_jid,
            [
                {
                    "app_ns": NS_JINGLE_FT,
                    "senders": self._j.ROLE_RESPONDER,
                    "app_kwargs": {
                        "filepath": filepath,
                        "name": name,
                        "extra": extra,
                        "progress_id_d": progress_id_d,
                    },
                }
            ],
        )
        progress_id = yield progress_id_d
        defer.returnValue(progress_id)

    # jingle callbacks

    def jingleSessionInit(
        self, client, session, content_name, filepath, name, extra, progress_id_d
    ):
        if extra is None:
            extra = {}
        else:
            if not EXTRA_ALLOWED.issuperset(extra):
                raise ValueError(
                    _(u"only the following keys are allowed in extra: {keys}").format(
                        keys=u", ".join(EXTRA_ALLOWED)
                    )
                )
        progress_id_d.callback(self.getProgressId(session, content_name))
        content_data = session["contents"][content_name]
        application_data = content_data["application_data"]
        assert "file_path" not in application_data
        application_data["file_path"] = filepath
        file_data = application_data["file_data"] = {}
        desc_elt = domish.Element((NS_JINGLE_FT, "description"))
        file_elt = desc_elt.addElement("file")

        if content_data[u"senders"] == self._j.ROLE_INITIATOR:
            # we send a file
            if name is None:
                name = os.path.basename(filepath)
            file_data[u"date"] = utils.xmpp_date()
            file_data[u"desc"] = extra.pop(u"file_desc", u"")
            file_data[u"name"] = name
            mime_type = mimetypes.guess_type(name, strict=False)[0]
            if mime_type is not None:
                file_data[u"mime_type"] = mime_type
            file_data[u"size"] = os.path.getsize(filepath)
            if u"namespace" in extra:
                file_data[u"namespace"] = extra[u"namespace"]
            if u"path" in extra:
                file_data[u"path"] = extra[u"path"]
            self.buildFileElementFromDict(file_data, file_elt=file_elt, file_hash=u"")
        else:
            # we request a file
            file_hash = extra.pop(u"file_hash", u"")
            if not name and not file_hash:
                raise ValueError(_(u"you need to provide at least name or file hash"))
            if name:
                file_data[u"name"] = name
            if file_hash:
                file_data[u"file_hash"] = file_hash
                file_data[u"hash_algo"] = extra[u"hash_algo"]
            else:
                file_data[u"hash_algo"] = self._hash.getDefaultAlgo()
            if u"namespace" in extra:
                file_data[u"namespace"] = extra[u"namespace"]
            if u"path" in extra:
                file_data[u"path"] = extra[u"path"]
            self.buildFileElementFromDict(file_data, file_elt=file_elt)

        return desc_elt

    def jingleRequestConfirmation(self, client, action, session, content_name, desc_elt):
        """This method request confirmation for a jingle session"""
        content_data = session["contents"][content_name]
        senders = content_data[u"senders"]
        if senders not in (self._j.ROLE_INITIATOR, self._j.ROLE_RESPONDER):
            log.warning(u"Bad sender, assuming initiator")
            senders = content_data[u"senders"] = self._j.ROLE_INITIATOR
        # first we grab file informations
        try:
            file_elt = desc_elt.elements(NS_JINGLE_FT, "file").next()
        except StopIteration:
            raise failure.Failure(exceptions.DataError)
        file_data = {"progress_id": self.getProgressId(session, content_name)}

        if senders == self._j.ROLE_RESPONDER:
            # we send the file
            return self._fileSendingRequestConf(
                client, session, content_data, content_name, file_data, file_elt
            )
        else:
            # we receive the file
            return self._fileReceivingRequestConf(
                client, session, content_data, content_name, file_data, file_elt
            )

    @defer.inlineCallbacks
    def _fileSendingRequestConf(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        """parse file_elt, and handle file retrieving/permission checking"""
        self.parseFileElement(file_elt, file_data)
        content_data["application_data"]["file_data"] = file_data
        finished_d = content_data["finished_d"] = defer.Deferred()

        # confirmed_d is a deferred returning confimed value (only used if cont is False)
        cont, confirmed_d = self.host.trigger.returnPoint(
            "XEP-0234_fileSendingRequest",
            client,
            session,
            content_data,
            content_name,
            file_data,
            file_elt,
        )
        if not cont:
            confirmed = yield confirmed_d
            if confirmed:
                args = [client, session, content_name, content_data]
                finished_d.addCallbacks(
                    self._finishedCb, self._finishedEb, args, None, args
                )
            defer.returnValue(confirmed)

        log.warning(_(u"File continue is not implemented yet"))
        defer.returnValue(False)

    def _fileReceivingRequestConf(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        """parse file_elt, and handle user permission/file opening"""
        self.parseFileElement(file_elt, file_data, given=True)
        try:
            hash_algo, file_data["given_file_hash"] = self._hash.parseHashElt(file_elt)
        except exceptions.NotFound:
            try:
                hash_algo = self._hash.parseHashUsedElt(file_elt)
            except exceptions.NotFound:
                raise failure.Failure(exceptions.DataError)

        if hash_algo is not None:
            file_data["hash_algo"] = hash_algo
            file_data["hash_hasher"] = hasher = self._hash.getHasher(hash_algo)
            file_data["data_cb"] = lambda data: hasher.update(data)

        try:
            file_data["size"] = int(file_data["size"])
        except ValueError:
            raise failure.Failure(exceptions.DataError)

        name = file_data["name"]
        if "/" in name or "\\" in name:
            log.warning(
                u"File name contain path characters, we replace them: {}".format(name)
            )
            file_data["name"] = name.replace("/", "_").replace("\\", "_")

        content_data["application_data"]["file_data"] = file_data

        # now we actualy request permission to user
        def gotConfirmation(confirmed):
            if confirmed:
                args = [client, session, content_name, content_data]
                finished_d.addCallbacks(
                    self._finishedCb, self._finishedEb, args, None, args
                )
            return confirmed

        # deferred to track end of transfer
        finished_d = content_data["finished_d"] = defer.Deferred()
        d = self._f.getDestDir(
            client, session["peer_jid"], content_data, file_data, stream_object=True
        )
        d.addCallback(gotConfirmation)
        return d

    def jingleHandler(self, client, action, session, content_name, desc_elt):
        content_data = session["contents"][content_name]
        application_data = content_data["application_data"]
        if action in (self._j.A_ACCEPTED_ACK,):
            pass
        elif action == self._j.A_SESSION_INITIATE:
            file_elt = desc_elt.elements(NS_JINGLE_FT, "file").next()
            try:
                file_elt.elements(NS_JINGLE_FT, "range").next()
            except StopIteration:
                # initiator doesn't manage <range>, but we do so we advertise it
                #  FIXME: to be checked
                log.debug("adding <range> element")
                file_elt.addElement("range")
        elif action == self._j.A_SESSION_ACCEPT:
            assert not "stream_object" in content_data
            file_data = application_data["file_data"]
            file_path = application_data["file_path"]
            senders = content_data[u"senders"]
            if senders != session[u"role"]:
                # we are receiving the file
                try:
                    # did the responder specified the size of the file?
                    file_elt = next(desc_elt.elements(NS_JINGLE_FT, u"file"))
                    size_elt = next(file_elt.elements(NS_JINGLE_FT, u"size"))
                    size = int(unicode(size_elt))
                except (StopIteration, ValueError):
                    size = None
                # XXX: hash security is not critical here, so we just take the higher mandatory one
                hasher = file_data["hash_hasher"] = self._hash.getHasher()
                content_data["stream_object"] = stream.FileStreamObject(
                    self.host,
                    client,
                    file_path,
                    mode="wb",
                    uid=self.getProgressId(session, content_name),
                    size=size,
                    data_cb=lambda data: hasher.update(data),
                )
            else:
                # we are sending the file
                size = file_data["size"]
                # XXX: hash security is not critical here, so we just take the higher mandatory one
                hasher = file_data["hash_hasher"] = self._hash.getHasher()
                content_data["stream_object"] = stream.FileStreamObject(
                    self.host,
                    client,
                    file_path,
                    uid=self.getProgressId(session, content_name),
                    size=size,
                    data_cb=lambda data: hasher.update(data),
                )
            finished_d = content_data["finished_d"] = defer.Deferred()
            args = [client, session, content_name, content_data]
            finished_d.addCallbacks(self._finishedCb, self._finishedEb, args, None, args)
        else:
            log.warning(u"FIXME: unmanaged action {}".format(action))
        return desc_elt

    def jingleSessionInfo(self, client, action, session, content_name, jingle_elt):
        """Called on session-info action

        manage checksum, and ignore <received/> element
        """
        # TODO: manage <received/> element
        content_data = session["contents"][content_name]
        elts = [elt for elt in jingle_elt.elements() if elt.uri == NS_JINGLE_FT]
        if not elts:
            return
        for elt in elts:
            if elt.name == "received":
                pass
            elif elt.name == "checksum":
                # we have received the file hash, we need to parse it
                if content_data["senders"] == session["role"]:
                    log.warning(
                        u"unexpected checksum received while we are the file sender"
                    )
                    raise exceptions.DataError
                info_content_name = elt["name"]
                if info_content_name != content_name:
                    # it was for an other content...
                    return
                file_data = content_data["application_data"]["file_data"]
                try:
                    file_elt = elt.elements((NS_JINGLE_FT, "file")).next()
                except StopIteration:
                    raise exceptions.DataError
                algo, file_data["given_file_hash"] = self._hash.parseHashElt(file_elt)
                if algo != file_data.get("hash_algo"):
                    log.warning(
                        u"Hash algorithm used in given hash ({peer_algo}) doesn't correspond to the one we have used ({our_algo}) [{profile}]".format(
                            peer_algo=algo,
                            our_algo=file_data.get("hash_algo"),
                            profile=client.profile,
                        )
                    )
                else:
                    self._receiverTryTerminate(
                        client, session, content_name, content_data
                    )
            else:
                raise NotImplementedError

    def jingleTerminate(self, client, action, session, content_name, jingle_elt):
        if jingle_elt.decline:
            # progress is the only way to tell to frontends that session has been declined
            progress_id = self.getProgressId(session, content_name)
            self.host.bridge.progressError(
                progress_id, C.PROGRESS_ERROR_DECLINED, client.profile
            )

    def _sendCheckSum(self, client, session, content_name, content_data):
        """Send the session-info with the hash checksum"""
        file_data = content_data["application_data"]["file_data"]
        hasher = file_data["hash_hasher"]
        hash_ = hasher.hexdigest()
        log.debug(u"Calculated hash: {}".format(hash_))
        iq_elt, jingle_elt = self._j.buildSessionInfo(client, session)
        checksum_elt = jingle_elt.addElement((NS_JINGLE_FT, "checksum"))
        checksum_elt["creator"] = content_data["creator"]
        checksum_elt["name"] = content_name
        file_elt = checksum_elt.addElement("file")
        file_elt.addChild(self._hash.buildHashElt(hash_))
        iq_elt.send()

    def _receiverTryTerminate(
        self, client, session, content_name, content_data, last_try=False
    ):
        """Try to terminate the session

        This method must only be used by the receiver.
        It check if transfer is finished, and hash available,
        if everything is OK, it check hash and terminate the session
        @param last_try(bool): if True this mean than session must be terminated even given hash is not available
        @return (bool): True if session was terminated
        """
        if not content_data.get("transfer_finished", False):
            return False
        file_data = content_data["application_data"]["file_data"]
        given_hash = file_data.get("given_file_hash")
        if given_hash is None:
            if last_try:
                log.warning(
                    u"sender didn't sent hash checksum, we can't check the file [{profile}]".format(
                        profile=client.profile
                    )
                )
                self._j.delayedContentTerminate(client, session, content_name)
                content_data["stream_object"].close()
                return True
            return False
        hasher = file_data["hash_hasher"]
        hash_ = hasher.hexdigest()

        if hash_ == given_hash:
            log.info(u"Hash checked, file was successfully transfered: {}".format(hash_))
            progress_metadata = {
                "hash": hash_,
                "hash_algo": file_data["hash_algo"],
                "hash_verified": C.BOOL_TRUE,
            }
            error = None
        else:
            log.warning(u"Hash mismatch, the file was not transfered correctly")
            progress_metadata = None
            error = u"Hash mismatch: given={algo}:{given}, calculated={algo}:{our}".format(
                algo=file_data["hash_algo"], given=given_hash, our=hash_
            )

        self._j.delayedContentTerminate(client, session, content_name)
        content_data["stream_object"].close(progress_metadata, error)
        # we may have the last_try timer still active, so we try to cancel it
        try:
            content_data["last_try_timer"].cancel()
        except (KeyError, internet_error.AlreadyCalled):
            pass
        return True

    def _finishedCb(self, __, client, session, content_name, content_data):
        log.info(u"File transfer terminated")
        if content_data["senders"] != session["role"]:
            # we terminate the session only if we are the receiver,
            # as recommanded in XEP-0234 §2 (after example 6)
            content_data["transfer_finished"] = True
            if not self._receiverTryTerminate(
                client, session, content_name, content_data
            ):
                # we have not received the hash yet, we wait 5 more seconds
                content_data["last_try_timer"] = reactor.callLater(
                    5,
                    self._receiverTryTerminate,
                    client,
                    session,
                    content_name,
                    content_data,
                    last_try=True,
                )
        else:
            # we are the sender, we send the checksum
            self._sendCheckSum(client, session, content_name, content_data)
            content_data["stream_object"].close()

    def _finishedEb(self, failure, client, session, content_name, content_data):
        log.warning(u"Error while streaming file: {}".format(failure))
        content_data["stream_object"].close()
        self._j.contentTerminate(
            client, session, content_name, reason=self._j.REASON_FAILED_TRANSPORT
        )


class XEP_0234_handler(XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_JINGLE_FT)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

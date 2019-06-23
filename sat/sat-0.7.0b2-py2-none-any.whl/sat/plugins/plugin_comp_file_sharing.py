#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for parrot mode (experimental)
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
from sat.tools.common import regex
from sat.tools.common import uri
from sat.tools import stream
from twisted.internet import defer
from twisted.words.protocols.jabber import error
from wokkel import pubsub
from wokkel import generic
from functools import partial
import os
import os.path
import mimetypes


PLUGIN_INFO = {
    C.PI_NAME: "File sharing component",
    C.PI_IMPORT_NAME: "file_sharing",
    C.PI_MODES: [C.PLUG_MODE_COMPONENT],
    C.PI_TYPE: C.PLUG_TYPE_ENTRY_POINT,
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [
        "FILE",
        "FILE_SHARING_MANAGEMENT",
        "XEP-0231",
        "XEP-0234",
        "XEP-0260",
        "XEP-0261",
        "XEP-0264",
        "XEP-0329",
    ],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: "FileSharing",
    C.PI_HANDLER: C.BOOL_TRUE,
    C.PI_DESCRIPTION: _(u"""Component hosting and sharing files"""),
}

HASH_ALGO = u"sha-256"
NS_COMMENTS = "org.salut-a-toi.comments"
COMMENT_NODE_PREFIX = "org.salut-a-toi.file_comments/"


class FileSharing(object):
    def __init__(self, host):
        log.info(_(u"File Sharing initialization"))
        self.host = host
        self._f = host.plugins["FILE"]
        self._jf = host.plugins["XEP-0234"]
        self._h = host.plugins["XEP-0300"]
        self._t = host.plugins["XEP-0264"]
        host.trigger.add("FILE_getDestDir", self._getDestDirTrigger)
        host.trigger.add(
            "XEP-0234_fileSendingRequest", self._fileSendingRequestTrigger, priority=1000
        )
        host.trigger.add("XEP-0234_buildFileElement", self._addFileComments)
        host.trigger.add("XEP-0234_parseFileElement", self._getFileComments)
        host.trigger.add("XEP-0329_compGetFilesFromNode", self._addCommentsData)
        self.files_path = host.getLocalPath(None, C.FILES_DIR, profile=False)

    def getHandler(self, client):
        return Comments_handler(self)

    def profileConnected(self, client):
        path = client.file_tmp_dir = os.path.join(
            self.host.memory.getConfig("", "local_dir"),
            C.FILES_TMP_DIR,
            regex.pathEscape(client.profile),
        )
        if not os.path.exists(path):
            os.makedirs(path)

    @defer.inlineCallbacks
    def _fileTransferedCb(self, __, client, peer_jid, file_data, file_path):
        """post file reception tasks

        on file is received, this method create hash/thumbnails if necessary
        move the file to the right location, and create metadata entry in database
        """
        name = file_data[u"name"]
        extra = {}

        if file_data[u"hash_algo"] == HASH_ALGO:
            log.debug(_(u"Reusing already generated hash"))
            file_hash = file_data[u"hash_hasher"].hexdigest()
        else:
            hasher = self._h.getHasher(HASH_ALGO)
            with open("file_path") as f:
                file_hash = yield self._h.calculateHash(f, hasher)
        final_path = os.path.join(self.files_path, file_hash)

        if os.path.isfile(final_path):
            log.debug(
                u"file [{file_hash}] already exists, we can remove temporary one".format(
                    file_hash=file_hash
                )
            )
            os.unlink(file_path)
        else:
            os.rename(file_path, final_path)
            log.debug(
                u"file [{file_hash}] moved to {files_path}".format(
                    file_hash=file_hash, files_path=self.files_path
                )
            )

        mime_type = file_data.get(u"mime_type")
        if not mime_type or mime_type == u"application/octet-stream":
            mime_type = mimetypes.guess_type(name)[0]

        if mime_type is not None and mime_type.startswith(u"image"):
            thumbnails = extra.setdefault(C.KEY_THUMBNAILS, [])
            for max_thumb_size in (self._t.SIZE_SMALL, self._t.SIZE_MEDIUM):
                try:
                    thumb_size, thumb_id = yield self._t.generateThumbnail(
                        final_path,
                        max_thumb_size,
                        #  we keep thumbnails for 6 months
                        60 * 60 * 24 * 31 * 6,
                    )
                except Exception as e:
                    log.warning(_(u"Can't create thumbnail: {reason}").format(reason=e))
                    break
                thumbnails.append({u"id": thumb_id, u"size": thumb_size})

        self.host.memory.setFile(
            client,
            name=name,
            version=u"",
            file_hash=file_hash,
            hash_algo=HASH_ALGO,
            size=file_data[u"size"],
            path=file_data.get(u"path"),
            namespace=file_data.get(u"namespace"),
            mime_type=mime_type,
            owner=peer_jid,
            extra=extra,
        )

    def _getDestDirTrigger(
        self, client, peer_jid, transfer_data, file_data, stream_object
    ):
        """This trigger accept file sending request, and store file locally"""
        if not client.is_component:
            return True, None
        assert stream_object
        assert "stream_object" not in transfer_data
        assert C.KEY_PROGRESS_ID in file_data
        filename = file_data["name"]
        assert filename and not "/" in filename
        file_tmp_dir = self.host.getLocalPath(
            client, C.FILES_TMP_DIR, peer_jid.userhost(), component=True, profile=False
        )
        file_tmp_path = file_data["file_path"] = os.path.join(
            file_tmp_dir, file_data["name"]
        )

        transfer_data["finished_d"].addCallback(
            self._fileTransferedCb, client, peer_jid, file_data, file_tmp_path
        )

        self._f.openFileWrite(
            client, file_tmp_path, transfer_data, file_data, stream_object
        )
        return False, defer.succeed(True)

    @defer.inlineCallbacks
    def _retrieveFiles(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        """This method retrieve a file on request, and send if after checking permissions"""
        peer_jid = session[u"peer_jid"]
        try:
            found_files = yield self.host.memory.getFiles(
                client,
                peer_jid=peer_jid,
                name=file_data.get(u"name"),
                file_hash=file_data.get(u"file_hash"),
                hash_algo=file_data.get(u"hash_algo"),
                path=file_data.get(u"path"),
                namespace=file_data.get(u"namespace"),
            )
        except exceptions.NotFound:
            found_files = None
        except exceptions.PermissionError:
            log.warning(
                _(u"{peer_jid} is trying to access an unauthorized file: {name}").format(
                    peer_jid=peer_jid, name=file_data.get(u"name")
                )
            )
            defer.returnValue(False)

        if not found_files:
            log.warning(
                _(u"no matching file found ({file_data})").format(file_data=file_data)
            )
            defer.returnValue(False)

        # we only use the first found file
        found_file = found_files[0]
        if found_file[u'type'] != C.FILE_TYPE_FILE:
            raise TypeError(u"a file was expected, type is {type_}".format(
                type_=found_file[u'type']))
        file_hash = found_file[u"file_hash"]
        file_path = os.path.join(self.files_path, file_hash)
        file_data[u"hash_hasher"] = hasher = self._h.getHasher(found_file[u"hash_algo"])
        size = file_data[u"size"] = found_file[u"size"]
        file_data[u"file_hash"] = file_hash
        file_data[u"hash_algo"] = found_file[u"hash_algo"]

        # we complete file_elt so peer can have some details on the file
        if u"name" not in file_data:
            file_elt.addElement(u"name", content=found_file[u"name"])
        file_elt.addElement(u"size", content=unicode(size))
        content_data["stream_object"] = stream.FileStreamObject(
            self.host,
            client,
            file_path,
            uid=self._jf.getProgressId(session, content_name),
            size=size,
            data_cb=lambda data: hasher.update(data),
        )
        defer.returnValue(True)

    def _fileSendingRequestTrigger(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        if not client.is_component:
            return True, None
        else:
            return (
                False,
                self._retrieveFiles(
                    client, session, content_data, content_name, file_data, file_elt
                ),
            )

    ## comments triggers ##

    def _addFileComments(self, file_elt, extra_args):
        try:
            comments_url = extra_args.pop("comments_url")
        except KeyError:
            return

        comment_elt = file_elt.addElement((NS_COMMENTS, "comments"), content=comments_url)

        try:
            count = len(extra_args[u"extra"][u"comments"])
        except KeyError:
            count = 0

        comment_elt["count"] = unicode(count)
        return True

    def _getFileComments(self, file_elt, file_data):
        try:
            comments_elt = next(file_elt.elements(NS_COMMENTS, "comments"))
        except StopIteration:
            return
        file_data["comments_url"] = unicode(comments_elt)
        file_data["comments_count"] = comments_elt["count"]
        return True

    def _addCommentsData(self, client, iq_elt, owner, node_path, files_data):
        for file_data in files_data:
            file_data["comments_url"] = uri.buildXMPPUri(
                "pubsub",
                path=client.jid.full(),
                node=COMMENT_NODE_PREFIX + file_data["id"],
            )
        return True


class Comments_handler(pubsub.PubSubService):
    """This class is a minimal Pubsub service handling virtual nodes for comments"""

    def __init__(self, plugin_parent):
        super(Comments_handler, self).__init__()  # PubsubVirtualResource())
        self.host = plugin_parent.host
        self.plugin_parent = plugin_parent
        self.discoIdentity = {
            "category": "pubsub",
            "type": "virtual",  # FIXME: non standard, here to avoid this service being considered as main pubsub one
            "name": "files commenting service",
        }

    def _getFileId(self, nodeIdentifier):
        if not nodeIdentifier.startswith(COMMENT_NODE_PREFIX):
            raise error.StanzaError("item-not-found")
        file_id = nodeIdentifier[len(COMMENT_NODE_PREFIX) :]
        if not file_id:
            raise error.StanzaError("item-not-found")
        return file_id

    @defer.inlineCallbacks
    def getFileData(self, requestor, nodeIdentifier):
        file_id = self._getFileId(nodeIdentifier)
        try:
            files = yield self.host.memory.getFiles(self.parent, requestor, file_id)
        except (exceptions.NotFound, exceptions.PermissionError):
            # we don't differenciate between NotFound and PermissionError
            # to avoid leaking information on existing files
            raise error.StanzaError("item-not-found")
        if not files:
            raise error.StanzaError("item-not-found")
        if len(files) > 1:
            raise error.InternalError("there should be only one file")
        defer.returnValue(files[0])

    def commentsUpdate(self, extra, new_comments, peer_jid):
        """update comments (replace or insert new_comments)

        @param extra(dict): extra data to update
        @param new_comments(list[tuple(unicode, unicode, unicode)]): comments to update or insert
        @param peer_jid(unicode, None): bare jid of the requestor, or None if request is done by owner
        """
        current_comments = extra.setdefault("comments", [])
        new_comments_by_id = {c[0]: c for c in new_comments}
        updated = []
        # we now check every current comment, to see if one id in new ones
        # exist, in which case we must update
        for idx, comment in enumerate(current_comments):
            comment_id = comment[0]
            if comment_id in new_comments_by_id:
                # a new comment has an existing id, update is requested
                if peer_jid and comment[1] != peer_jid:
                    # requestor has not the right to modify the comment
                    raise exceptions.PermissionError
                # we replace old_comment with updated one
                new_comment = new_comments_by_id[comment_id]
                current_comments[idx] = new_comment
                updated.append(new_comment)

        # we now remove every updated comments, to only keep
        # the ones to insert
        for comment in updated:
            new_comments.remove(comment)

        current_comments.extend(new_comments)

    def commentsDelete(self, extra, comments):
        try:
            comments_dict = extra["comments"]
        except KeyError:
            return
        for comment in comments:
            try:
                comments_dict.remove(comment)
            except ValueError:
                continue

    def _getFrom(self, item_elt):
        """retrieve published of an item

        @param item_elt(domish.element): <item> element
        @return (unicode): full jid as string
        """
        iq_elt = item_elt
        while iq_elt.parent != None:
            iq_elt = iq_elt.parent
        return iq_elt["from"]

    @defer.inlineCallbacks
    def publish(self, requestor, service, nodeIdentifier, items):
        #  we retrieve file a first time to check authorisations
        file_data = yield self.getFileData(requestor, nodeIdentifier)
        file_id = file_data["id"]
        comments = [(item["id"], self._getFrom(item), item.toXml()) for item in items]
        if requestor.userhostJID() == file_data["owner"]:
            peer_jid = None
        else:
            peer_jid = requestor.userhost()
        update_cb = partial(self.commentsUpdate, new_comments=comments, peer_jid=peer_jid)
        try:
            yield self.host.memory.fileUpdate(file_id, "extra", update_cb)
        except exceptions.PermissionError:
            raise error.StanzaError("not-authorized")

    @defer.inlineCallbacks
    def items(self, requestor, service, nodeIdentifier, maxItems, itemIdentifiers):
        file_data = yield self.getFileData(requestor, nodeIdentifier)
        comments = file_data["extra"].get("comments", [])
        if itemIdentifiers:
            defer.returnValue(
                [generic.parseXml(c[2]) for c in comments if c[0] in itemIdentifiers]
            )
        else:
            defer.returnValue([generic.parseXml(c[2]) for c in comments])

    @defer.inlineCallbacks
    def retract(self, requestor, service, nodeIdentifier, itemIdentifiers):
        file_data = yield self.getFileData(requestor, nodeIdentifier)
        file_id = file_data["id"]
        try:
            comments = file_data["extra"]["comments"]
        except KeyError:
            raise error.StanzaError("item-not-found")

        to_remove = []
        for comment in comments:
            comment_id = comment[0]
            if comment_id in itemIdentifiers:
                to_remove.append(comment)
                itemIdentifiers.remove(comment_id)
                if not itemIdentifiers:
                    break

        if itemIdentifiers:
            # not all items have been to_remove, we can't continue
            raise error.StanzaError("item-not-found")

        if requestor.userhostJID() != file_data["owner"]:
            if not all([c[1] == requestor.userhost() for c in to_remove]):
                raise error.StanzaError("not-authorized")

        remove_cb = partial(self.commentsDelete, comments=to_remove)
        yield self.host.memory.fileUpdate(file_id, "extra", remove_cb)

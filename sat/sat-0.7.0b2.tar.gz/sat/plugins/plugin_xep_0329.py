#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for File Information Sharing (XEP-0329)
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

log = getLogger(__name__)
from sat.tools import stream
from sat.tools.common import regex
from wokkel import disco, iwokkel
from zope.interface import implements
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as jabber_error
from twisted.internet import defer
import mimetypes
import json
import os


PLUGIN_INFO = {
    C.PI_NAME: "File Information Sharing",
    C.PI_IMPORT_NAME: "XEP-0329",
    C.PI_TYPE: "XEP",
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_PROTOCOLS: ["XEP-0329"],
    C.PI_DEPENDENCIES: ["XEP-0234", "XEP-0300", "XEP-0106"],
    C.PI_MAIN: "XEP_0329",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _(u"""Implementation of File Information Sharing"""),
}

NS_FIS = "urn:xmpp:fis:0"

IQ_FIS_REQUEST = C.IQ_GET + '/query[@xmlns="' + NS_FIS + '"]'
SINGLE_FILES_DIR = u"files"
TYPE_VIRTUAL = u"virtual"
TYPE_PATH = u"path"
SHARE_TYPES = (TYPE_PATH, TYPE_VIRTUAL)
KEY_TYPE = u"type"


class ShareNode(object):
    """Node containing directory or files to share, virtual or real"""

    host = None

    def __init__(self, name, parent, type_, access, path=None):
        assert type_ in SHARE_TYPES
        if name is not None:
            if name == u".." or u"/" in name or u"\\" in name:
                log.warning(
                    _(u"path change chars found in name [{name}], hack attempt?").format(
                        name=name
                    )
                )
                if name == u"..":
                    name = u"--"
                else:
                    name = regex.pathEscape(name)
        self.name = name
        self.children = {}
        self.type = type_
        self.access = {} if access is None else access
        assert isinstance(self.access, dict)
        self.parent = None
        if parent is not None:
            assert name
            parent.addChild(self)
        else:
            assert name is None
        if path is not None:
            if type_ != TYPE_PATH:
                raise exceptions.InternalError(_(u"path can only be set on path nodes"))
            self._path = path

    @property
    def path(self):
        return self._path

    def __getitem__(self, key):
        return self.children[key]

    def __contains__(self, item):
        return self.children.__contains__(item)

    def __iter__(self):
        return self.children.__iter__()

    def iteritems(self):
        return self.children.iteritems()

    def itervalues(self):
        return self.children.itervalues()

    def getOrCreate(self, name, type_=TYPE_VIRTUAL, access=None):
        """Get a node or create a virtual node and return it"""
        if access is None:
            access = {C.ACCESS_PERM_READ: {KEY_TYPE: C.ACCESS_TYPE_PUBLIC}}
        try:
            return self.children[name]
        except KeyError:
            node = ShareNode(name, self, type_=type_, access=access)
            return node

    def addChild(self, node):
        if node.parent is not None:
            raise exceptions.ConflictError(_(u"a node can't have several parents"))
        node.parent = self
        self.children[node.name] = node

    def removeFromParent(self):
        try:
            del self.parent.children[self.name]
        except TypeError:
            raise exceptions.InternalError(
                u"trying to remove a node from inexisting parent"
            )
        except KeyError:
            raise exceptions.InternalError(u"node not found in parent's children")
        self.parent = None

    def _checkNodePermission(self, client, node, perms, peer_jid):
        """Check access to this node for peer_jid

        @param node(SharedNode): node to check access
        @param perms(unicode): permissions to check, iterable of C.ACCESS_PERM_*
        @param peer_jid(jid.JID): entity which try to access the node
        @return (bool): True if entity can access
        """
        file_data = {u"access": self.access, u"owner": client.jid.userhostJID()}
        try:
            self.host.memory.checkFilePermission(file_data, peer_jid, perms)
        except exceptions.PermissionError:
            return False
        else:
            return True

    def checkPermissions(
        self, client, peer_jid, perms=(C.ACCESS_PERM_READ,), check_parents=True
    ):
        """Check that peer_jid can access this node and all its parents

        @param peer_jid(jid.JID): entrity trying to access the node
        @param perms(unicode): permissions to check, iterable of C.ACCESS_PERM_*
        @param check_parents(bool): if True, access of all parents of this node will be
            checked too
        @return (bool): True if entity can access this node
        """
        peer_jid = peer_jid.userhostJID()
        if peer_jid == client.jid.userhostJID():
            return True

        parent = self
        while parent != None:
            if not self._checkNodePermission(client, parent, perms, peer_jid):
                return False
            parent = parent.parent

        return True

    @staticmethod
    def find(client, path, peer_jid, perms=(C.ACCESS_PERM_READ,)):
        """find node corresponding to a path

        @param path(unicode): path to the requested file or directory
        @param peer_jid(jid.JID): entity trying to find the node
            used to check permission
        @return (dict, unicode): shared data, remaining path
        @raise exceptions.PermissionError: user can't access this file
        @raise exceptions.DataError: path is invalid
        @raise NotFound: path lead to a non existing file/directory
        """
        path_elts = filter(None, path.split(u"/"))

        if u".." in path_elts:
            log.warning(_(
                u'parent dir ("..") found in path, hack attempt? path is {path} '
                u'[{profile}]').format(path=path, profile=client.profile))
            raise exceptions.PermissionError(u"illegal path elements")

        if not path_elts:
            raise exceptions.DataError(_(u"path is invalid: {path}").format(path=path))

        node = client._XEP_0329_root_node

        while path_elts:
            if node.type == TYPE_VIRTUAL:
                try:
                    node = node[path_elts.pop(0)]
                except KeyError:
                    raise exceptions.NotFound
            elif node.type == TYPE_PATH:
                break

        if not node.checkPermissions(client, peer_jid, perms=perms):
            raise exceptions.PermissionError(u"permission denied")

        return node, u"/".join(path_elts)

    def findByLocalPath(self, path):
        """retrieve nodes linking to local path

        @return (list[ShareNode]): found nodes associated to path
        @raise exceptions.NotFound: no node has been found with this path
        """
        shared_paths = self.getSharedPaths()
        try:
            return shared_paths[path]
        except KeyError:
            raise exceptions.NotFound

    def _getSharedPaths(self, node, paths):
        if node.type == TYPE_VIRTUAL:
            for node in node.itervalues():
                self._getSharedPaths(node, paths)
        elif node.type == TYPE_PATH:
            paths.setdefault(node.path, []).append(node)
        else:
            raise exceptions.InternalError(
                u"unknown node type: {type}".format(type=node.type)
            )

    def getSharedPaths(self):
        """retrieve nodes by shared path

        this method will retrieve recursively shared path in children of this node
        @return (dict): map from shared path to list of nodes
        """
        if self.type == TYPE_PATH:
            raise exceptions.InternalError(
                "getSharedPaths must be used on a virtual node"
            )
        paths = {}
        self._getSharedPaths(self, paths)
        return paths


class XEP_0329(object):
    def __init__(self, host):
        log.info(_("File Information Sharing initialization"))
        self.host = host
        ShareNode.host = host
        self._h = host.plugins["XEP-0300"]
        self._jf = host.plugins["XEP-0234"]
        host.bridge.addMethod(
            "FISList",
            ".plugin",
            in_sign="ssa{ss}s",
            out_sign="aa{ss}",
            method=self._listFiles,
            async=True,
        )
        host.bridge.addMethod(
            "FISLocalSharesGet",
            ".plugin",
            in_sign="s",
            out_sign="as",
            method=self._localSharesGet,
        )
        host.bridge.addMethod(
            "FISSharePath",
            ".plugin",
            in_sign="ssss",
            out_sign="s",
            method=self._sharePath,
        )
        host.bridge.addMethod(
            "FISUnsharePath",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self._unsharePath,
        )
        host.bridge.addSignal("FISSharedPathNew", ".plugin", signature="sss")
        host.bridge.addSignal("FISSharedPathRemoved", ".plugin", signature="ss")
        host.trigger.add("XEP-0234_fileSendingRequest", self._fileSendingRequestTrigger)
        host.registerNamespace("fis", NS_FIS)

    def getHandler(self, client):
        return XEP_0329_handler(self)

    def profileConnected(self, client):
        if not client.is_component:
            client._XEP_0329_root_node = ShareNode(
                None,
                None,
                TYPE_VIRTUAL,
                {C.ACCESS_PERM_READ: {KEY_TYPE: C.ACCESS_TYPE_PUBLIC}},
            )
            client._XEP_0329_names_data = {}  #  name to share map

    def _fileSendingRequestTrigger(
        self, client, session, content_data, content_name, file_data, file_elt
    ):
        """This trigger check that a requested file is available, and fill suitable data

        Path and name are used to retrieve the file. If path is missing, we try our luck
        with known names
        """
        if client.is_component:
            return True, None

        try:
            name = file_data[u"name"]
        except KeyError:
            return True, None
        assert u"/" not in name

        path = file_data.get(u"path")
        if path is not None:
            # we have a path, we can follow it to find node
            try:
                node, rem_path = ShareNode.find(client, path, session[u"peer_jid"])
            except (exceptions.PermissionError, exceptions.NotFound):
                #  no file, or file not allowed, we continue normal workflow
                return True, None
            except exceptions.DataError:
                log.warning(_(u"invalid path: {path}").format(path=path))
                return True, None

            if node.type == TYPE_VIRTUAL:
                # we have a virtual node, so name must link to a path node
                try:
                    path = node[name].path
                except KeyError:
                    return True, None
            elif node.type == TYPE_PATH:
                # we have a path node, so we can retrieve the full path now
                path = os.path.join(node.path, rem_path, name)
            else:
                raise exceptions.InternalError(
                    u"unknown type: {type}".format(type=node.type)
                )
            if not os.path.exists(path):
                return True, None
            size = os.path.getsize(path)
        else:
            # we don't have the path, we try to find the file by its name
            try:
                name_data = client._XEP_0329_names_data[name]
            except KeyError:
                return True, None

            for path, shared_file in name_data.iteritems():
                if True:  #  FIXME: filters are here
                    break
            else:
                return True, None
            parent_node = shared_file[u"parent"]
            if not parent_node.checkPermissions(client, session[u"peer_jid"]):
                log.warning(
                    _(
                        u"{peer_jid} requested a file (s)he can't access [{profile}]"
                    ).format(peer_jid=session[u"peer_jid"], profile=client.profile)
                )
                return True, None
            size = shared_file[u"size"]

        file_data[u"size"] = size
        file_elt.addElement(u"size", content=unicode(size))
        hash_algo = file_data[u"hash_algo"] = self._h.getDefaultAlgo()
        hasher = file_data[u"hash_hasher"] = self._h.getHasher(hash_algo)
        file_elt.addChild(self._h.buildHashUsedElt(hash_algo))
        content_data["stream_object"] = stream.FileStreamObject(
            self.host,
            client,
            path,
            uid=self._jf.getProgressId(session, content_name),
            size=size,
            data_cb=lambda data: hasher.update(data),
        )
        return False, True

    # common methods

    def _requestHandler(self, client, iq_elt, root_nodes_cb, files_from_node_cb):
        iq_elt.handled = True
        node = iq_elt.query.getAttribute("node")
        if not node:
            d = defer.maybeDeferred(root_nodes_cb, client, iq_elt)
        else:
            d = defer.maybeDeferred(files_from_node_cb, client, iq_elt, node)
        d.addErrback(
            lambda failure_: log.error(
                _(u"error while retrieving files: {msg}").format(msg=failure_)
            )
        )

    def _iqError(self, client, iq_elt, condition="item-not-found"):
        error_elt = jabber_error.StanzaError(condition).toResponse(iq_elt)
        client.send(error_elt)

    #  client

    def _addPathData(self, client, query_elt, path, parent_node):
        """Fill query_elt with files/directories found in path"""
        name = os.path.basename(path)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            mime_type = mimetypes.guess_type(path, strict=False)[0]
            file_elt = self._jf.buildFileElement(
                name=name, size=size, mime_type=mime_type, modified=os.path.getmtime(path)
            )

            query_elt.addChild(file_elt)
            # we don't specify hash as it would be too resource intensive to calculate
            # it for all files.
            # we add file to name_data, so users can request it later
            name_data = client._XEP_0329_names_data.setdefault(name, {})
            if path not in name_data:
                name_data[path] = {
                    "size": size,
                    "mime_type": mime_type,
                    "parent": parent_node,
                }
        else:
            # we have a directory
            directory_elt = query_elt.addElement("directory")
            directory_elt["name"] = name

    def _pathNodeHandler(self, client, iq_elt, query_elt, node, path):
        """Fill query_elt for path nodes, i.e. physical directories"""
        path = os.path.join(node.path, path)

        if not os.path.exists(path):
            # path may have been moved since it has been shared
            return self._iqError(client, iq_elt)
        elif os.path.isfile(path):
            self._addPathData(client, query_elt, path, node)
        else:
            for name in sorted(os.listdir(path.encode("utf-8")), key=lambda n: n.lower()):
                try:
                    name = name.decode("utf-8", "strict")
                except UnicodeDecodeError as e:
                    log.warning(
                        _(u"ignoring invalid unicode name ({name}): {msg}").format(
                            name=name.decode("utf-8", "replace"), msg=e
                        )
                    )
                    continue
                full_path = os.path.join(path, name)
                self._addPathData(client, query_elt, full_path, node)

    def _virtualNodeHandler(self, client, peer_jid, iq_elt, query_elt, node):
        """Fill query_elt for virtual nodes"""
        for name, child_node in node.iteritems():
            if not child_node.checkPermissions(client, peer_jid, check_parents=False):
                continue
            node_type = child_node.type
            if node_type == TYPE_VIRTUAL:
                directory_elt = query_elt.addElement("directory")
                directory_elt["name"] = name
            elif node_type == TYPE_PATH:
                self._addPathData(client, query_elt, child_node.path, child_node)
            else:
                raise exceptions.InternalError(
                    _(u"unexpected type: {type}").format(type=node_type)
                )

    def _getRootNodesCb(self, client, iq_elt):
        peer_jid = jid.JID(iq_elt["from"])
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        for name, node in client._XEP_0329_root_node.iteritems():
            if not node.checkPermissions(client, peer_jid, check_parents=False):
                continue
            directory_elt = query_elt.addElement("directory")
            directory_elt["name"] = name
        client.send(iq_result_elt)

    def _getFilesFromNodeCb(self, client, iq_elt, node_path):
        """Main method to retrieve files/directories from a node_path"""
        peer_jid = jid.JID(iq_elt[u"from"])
        try:
            node, path = ShareNode.find(client, node_path, peer_jid)
        except (exceptions.PermissionError, exceptions.NotFound):
            return self._iqError(client, iq_elt)
        except exceptions.DataError:
            return self._iqError(client, iq_elt, condition="not-acceptable")

        node_type = node.type
        peer_jid = jid.JID(iq_elt["from"])
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        query_elt[u"node"] = node_path

        # we now fill query_elt according to node_type
        if node_type == TYPE_PATH:
            #  it's a physical path
            self._pathNodeHandler(client, iq_elt, query_elt, node, path)
        elif node_type == TYPE_VIRTUAL:
            assert not path
            self._virtualNodeHandler(client, peer_jid, iq_elt, query_elt, node)
        else:
            raise exceptions.InternalError(
                _(u"unknown node type: {type}").format(type=node_type)
            )

        client.send(iq_result_elt)

    def onRequest(self, iq_elt, client):
        return self._requestHandler(
            client, iq_elt, self._getRootNodesCb, self._getFilesFromNodeCb
        )

    # Component

    def _compParseJids(self, client, iq_elt):
        """Retrieve peer_jid and owner to use from IQ stanza

        @param iq_elt(domish.Element): IQ stanza of the FIS request
        @return (tuple[jid.JID, jid.JID]): peer_jid and owner
        """
        to_jid = jid.JID(iq_elt['to'])
        if to_jid.user:
            user = self.host.plugins['XEP-0106'].unescape(to_jid.user)
            if u'@' in user:
                # a full jid is specified
                owner = jid.JID(user)
            else:
                # only user part is specified, we use our own host to build the full jid
                owner = jid.JID(None, (user, client.host, None))
        else:
            owner = jid.JID(iq_elt["from"]).userhostJID()

        peer_jid = jid.JID(iq_elt["from"])
        return peer_jid, owner

    @defer.inlineCallbacks
    def _compGetRootNodesCb(self, client, iq_elt):
        peer_jid, owner = self._compParseJids(client, iq_elt)
        files_data = yield self.host.memory.getFiles(
            client,
            peer_jid=peer_jid,
            parent=u"",
            type_=C.FILE_TYPE_DIRECTORY,
            owner=owner,
        )
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        for file_data in files_data:
            name = file_data[u"name"]
            directory_elt = query_elt.addElement(u"directory")
            directory_elt[u"name"] = name
        client.send(iq_result_elt)

    @defer.inlineCallbacks
    def _compGetFilesFromNodeCb(self, client, iq_elt, node_path):
        """Retrieve files from local files repository according to permissions

        result stanza is then built and sent to requestor
        @trigger XEP-0329_compGetFilesFromNode(client, iq_elt, owner, node_path,
                                               files_data):
            can be used to add data/elements
        """
        peer_jid, owner = self._compParseJids(client, iq_elt)
        try:
            files_data = yield self.host.memory.getFiles(
                client, peer_jid=peer_jid, path=node_path, owner=owner
            )
        except exceptions.NotFound:
            self._iqError(client, iq_elt)
            return
        except exceptions.PermissionError:
            self._iqError(client, iq_elt, condition='not-allowed')
            return
        except Exception as e:
            log.error(u"internal server error: {e}".format(e=e))
            self._iqError(client, iq_elt, condition='internal-server-error')
            return
        iq_result_elt = xmlstream.toResponse(iq_elt, "result")
        query_elt = iq_result_elt.addElement((NS_FIS, "query"))
        query_elt[u"node"] = node_path
        if not self.host.trigger.point(
            u"XEP-0329_compGetFilesFromNode", client, iq_elt, owner, node_path, files_data
        ):
            return
        for file_data in files_data:
            file_elt = self._jf.buildFileElementFromDict(
                file_data, modified=file_data.get(u"modified", file_data[u"created"])
            )
            query_elt.addChild(file_elt)
        client.send(iq_result_elt)

    def onComponentRequest(self, iq_elt, client):
        return self._requestHandler(
            client, iq_elt, self._compGetRootNodesCb, self._compGetFilesFromNodeCb
        )

    def _parseResult(self, iq_elt):
        query_elt = next(iq_elt.elements(NS_FIS, "query"))
        files = []

        for elt in query_elt.elements():
            if elt.name == "file":
                # we have a file
                try:
                    file_data = self._jf.parseFileElement(elt)
                except exceptions.DataError:
                    continue
                file_data[u"type"] = C.FILE_TYPE_FILE
            elif elt.name == "directory" and elt.uri == NS_FIS:
                # we have a directory

                file_data = {"name": elt["name"], "type": C.FILE_TYPE_DIRECTORY}
            else:
                log.warning(
                    _(u"unexpected element, ignoring: {elt}").format(elt=elt.toXml())
                )
                continue
            files.append(file_data)
        return files

    # file methods #

    def _serializeData(self, files_data):
        for file_data in files_data:
            for key, value in file_data.iteritems():
                file_data[key] = (
                    json.dumps(value) if key in ("extra",) else unicode(value)
                )
        return files_data

    def _listFiles(self, target_jid, path, extra, profile):
        client = self.host.getClient(profile)
        target_jid = client.jid.userhostJID() if not target_jid else jid.JID(target_jid)
        d = self.listFiles(client, target_jid, path or None)
        d.addCallback(self._serializeData)
        return d

    def listFiles(self, client, target_jid, path=None, extra=None):
        """List file shared by an entity

        @param target_jid(jid.JID): jid of the sharing entity
        @param path(unicode, None): path to the directory containing shared files
            None to get root directories
        @param extra(dict, None): extra data
        @return list(dict): shared files
        """
        iq_elt = client.IQ("get")
        iq_elt["to"] = target_jid.full()
        query_elt = iq_elt.addElement((NS_FIS, "query"))
        if path:
            query_elt["node"] = path
        d = iq_elt.send()
        d.addCallback(self._parseResult)
        return d

    def _localSharesGet(self, profile):
        client = self.host.getClient(profile)
        return self.localSharesGet(client)

    def localSharesGet(self, client):
        return client._XEP_0329_root_node.getSharedPaths().keys()

    def _sharePath(self, name, path, access, profile):
        client = self.host.getClient(profile)
        access = json.loads(access)
        return self.sharePath(client, name or None, path, access)

    def sharePath(self, client, name, path, access):
        if client.is_component:
            raise exceptions.ClientTypeError
        if not os.path.exists(path):
            raise ValueError(_(u"This path doesn't exist!"))
        if not path or not path.strip(u" /"):
            raise ValueError(_(u"A path need to be specified"))
        if not isinstance(access, dict):
            raise ValueError(_(u"access must be a dict"))

        node = client._XEP_0329_root_node
        node_type = TYPE_PATH
        if os.path.isfile(path):
            # we have a single file, the workflow is diferrent as we store all single
            # files in the same dir
            node = node.getOrCreate(SINGLE_FILES_DIR)

        if not name:
            name = os.path.basename(path.rstrip(u" /"))
            if not name:
                raise exceptions.InternalError(_(u"Can't find a proper name"))

        if name in node or name == SINGLE_FILES_DIR:
            idx = 1
            new_name = name + "_" + unicode(idx)
            while new_name in node:
                idx += 1
                new_name = name + "_" + unicode(idx)
            name = new_name
            log.info(_(
                u"A directory with this name is already shared, renamed to {new_name} "
                u"[{profile}]".format( new_name=new_name, profile=client.profile)))

        ShareNode(name=name, parent=node, type_=node_type, access=access, path=path)
        self.host.bridge.FISSharedPathNew(path, name, client.profile)
        return name

    def _unsharePath(self, path, profile):
        client = self.host.getClient(profile)
        return self.unsharePath(client, path)

    def unsharePath(self, client, path):
        nodes = client._XEP_0329_root_node.findByLocalPath(path)
        for node in nodes:
            node.removeFromParent()
        self.host.bridge.FISSharedPathRemoved(path, client.profile)


class XEP_0329_handler(xmlstream.XMPPHandler):
    implements(iwokkel.IDisco)

    def __init__(self, plugin_parent):
        self.plugin_parent = plugin_parent
        self.host = plugin_parent.host

    def connectionInitialized(self):
        if self.parent.is_component:
            self.xmlstream.addObserver(
                IQ_FIS_REQUEST, self.plugin_parent.onComponentRequest, client=self.parent
            )
        else:
            self.xmlstream.addObserver(
                IQ_FIS_REQUEST, self.plugin_parent.onRequest, client=self.parent
            )

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(NS_FIS)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []

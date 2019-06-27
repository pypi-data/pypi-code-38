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

import os.path
from functools import partial
from sat.core.i18n import _, D_
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from wokkel import data_form
from twisted.internet import defer
from twisted.words.protocols.jabber import jid

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: u"File Sharing Management",
    C.PI_IMPORT_NAME: u"FILE_SHARING_MANAGEMENT",
    C.PI_MODES: [C.PLUG_MODE_COMPONENT],
    C.PI_TYPE: u"EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [u"XEP-0050", u"XEP-0264"],
    C.PI_RECOMMENDATIONS: [],
    C.PI_MAIN: u"FileSharingManagement",
    C.PI_HANDLER: u"no",
    C.PI_DESCRIPTION: _(
        u"Experimental handling of file management for file sharing. This plugins allows "
        u"to change permissions of stored files/directories or remove them."
    ),
}

NS_FILE_MANAGEMENT = u"https://salut-a-toi.org/protocol/file-management:0"
NS_FILE_MANAGEMENT_PERM = u"https://salut-a-toi.org/protocol/file-management:0#perm"
NS_FILE_MANAGEMENT_DELETE = u"https://salut-a-toi.org/protocol/file-management:0#delete"
NS_FILE_MANAGEMENT_THUMB = u"https://salut-a-toi.org/protocol/file-management:0#thumb"


class WorkflowError(Exception):
    """Raised when workflow can't be completed"""

    def __init__(self, err_args):
        """
        @param err_args(tuple): arguments to return to finish the command workflow
        """
        Exception.__init__(self)
        self.err_args = err_args


class FileSharingManagement(object):
    # This is a temporary way (Q&D) to handle stored files, a better way (using pubsub
    # syntax?) should be elaborated and proposed as a standard.

    def __init__(self, host):
        log.info(_(u"File Sharing Management plugin initialization"))
        self.host = host
        self._c = host.plugins["XEP-0050"]
        self._t = host.plugins["XEP-0264"]
        self.files_path = host.getLocalPath(None, C.FILES_DIR, profile=False)

    def profileConnected(self, client):
        self._c.addAdHocCommand(
            client, self._onChangeFile, u"Change Permissions of File(s)",
            node=NS_FILE_MANAGEMENT_PERM,
            allowed_magics=C.ENTITY_ALL,
        )
        self._c.addAdHocCommand(
            client, self._onDeleteFile, u"Delete File(s)",
            node=NS_FILE_MANAGEMENT_DELETE,
            allowed_magics=C.ENTITY_ALL,
        )
        self._c.addAdHocCommand(
            client, self._onGenThumbnails, u"Generate Thumbnails",
            node=NS_FILE_MANAGEMENT_THUMB,
            allowed_magics=C.ENTITY_ALL,
        )

    def _err(self, reason):
        """Helper method to get argument to return for error

        workflow will be interrupted with an error note
        @param reason(unicode): reason of the error
        @return (tuple): arguments to use in defer.returnValue
        """
        status = self._c.STATUS.COMPLETED
        payload = None
        note = (self._c.NOTE.ERROR, reason)
        return payload, status, None, note

    def _getRootArgs(self):
        """Create the form to select the file to use

        @return (tuple): arguments to use in defer.returnValue
        """
        status = self._c.STATUS.EXECUTING
        form = data_form.Form("form", title=u"File Management",
                              formNamespace=NS_FILE_MANAGEMENT)

        field = data_form.Field(
            "text-single", "path", required=True
        )
        form.addField(field)

        field = data_form.Field(
            "text-single", "namespace", required=False
        )
        form.addField(field)

        payload = form.toElement()
        return payload, status, None, None

    @defer.inlineCallbacks
    def _getFileData(self, client, session_data, command_form):
        """Retrieve field requested in root form

        "found_file" will also be set in session_data
        @param command_form(data_form.Form): response to root form
        @return (D(dict)): found file data
        @raise WorkflowError: something is wrong
        """
        fields = command_form.fields
        try:
            path = fields[u'path'].value.strip()
            namespace = fields[u'namespace'].value or None
        except KeyError:
            self._c.adHocError(self._c.ERROR.BAD_PAYLOAD)

        if not path:
            self._c.adHocError(self._c.ERROR.BAD_PAYLOAD)

        requestor = session_data[u'requestor']
        requestor_bare = requestor.userhostJID()
        path = path.rstrip(u'/')
        parent_path, basename = os.path.split(path)

        # TODO: if parent_path and basename are empty, we ask for root directory
        #       this must be managed

        try:
            found_files = yield self.host.memory.getFiles(
                client, requestor_bare, path=parent_path, name=basename,
                namespace=namespace)
            found_file = found_files[0]
        except (exceptions.NotFound, IndexError):
            raise WorkflowError(self._err(_(u"file not found")))
        except exceptions.PermissionError:
            raise WorkflowError(self._err(_(u"forbidden")))

        if found_file['owner'] != requestor_bare:
            # only owner can manage files
            log.warning(_(u"Only owner can manage files"))
            raise WorkflowError(self._err(_(u"forbidden")))

        session_data[u'found_file'] = found_file
        session_data[u'namespace'] = namespace
        defer.returnValue(found_file)

    def _updateReadPermission(self, access, allowed_jids):
        if not allowed_jids:
            if C.ACCESS_PERM_READ in access:
                del access[C.ACCESS_PERM_READ]
        elif allowed_jids == u'PUBLIC':
            access[C.ACCESS_PERM_READ] = {
                u"type": C.ACCESS_TYPE_PUBLIC
            }
        else:
            access[C.ACCESS_PERM_READ] = {
                u"type": C.ACCESS_TYPE_WHITELIST,
                u"jids": [j.full() for j in allowed_jids]
            }

    @defer.inlineCallbacks
    def _updateDir(self, client, requestor, namespace, file_data, allowed_jids):
        """Recursively update permission of a directory and all subdirectories

        @param file_data(dict): metadata of the file
        @param allowed_jids(list[jid.JID]): list of entities allowed to read the file
        """
        assert file_data[u'type'] == C.FILE_TYPE_DIRECTORY
        files_data = yield self.host.memory.getFiles(
            client, requestor, parent=file_data[u'id'], namespace=namespace)

        for file_data in files_data:
            if not file_data[u'access'].get(C.ACCESS_PERM_READ, {}):
                log.debug(u"setting {perm} read permission for {name}".format(
                    perm=allowed_jids, name=file_data[u'name']))
                yield self.host.memory.fileUpdate(
                    file_data[u'id'], u'access',
                    partial(self._updateReadPermission, allowed_jids=allowed_jids))
            if file_data[u'type'] == C.FILE_TYPE_DIRECTORY:
                yield self._updateDir(client, requestor, namespace, file_data, u'PUBLIC')

    @defer.inlineCallbacks
    def _onChangeFile(self, client, command_elt, session_data, action, node):
        try:
            x_elt = command_elt.elements(data_form.NS_X_DATA, "x").next()
            command_form = data_form.Form.fromElement(x_elt)
        except StopIteration:
            command_form = None

        found_file = session_data.get('found_file')
        requestor = session_data[u'requestor']
        requestor_bare = requestor.userhostJID()

        if command_form is None or len(command_form.fields) == 0:
            # root request
            defer.returnValue(self._getRootArgs())

        elif found_file is None:
            # file selected, we retrieve it and ask for permissions
            try:
                found_file = yield self._getFileData(client, session_data, command_form)
            except WorkflowError as e:
                defer.returnValue(e.err_args)

            # management request
            if found_file[u'type'] == C.FILE_TYPE_DIRECTORY:
                instructions = D_(u"Please select permissions for this directory")
            else:
                instructions = D_(u"Please select permissions for this file")

            form = data_form.Form("form", title=u"File Management",
                                  instructions=[instructions],
                                  formNamespace=NS_FILE_MANAGEMENT)
            field = data_form.Field(
                "text-multi", "read_allowed", required=False,
                desc=u'list of jids allowed to read this file (beside yourself), or '
                     u'"PUBLIC" to let a public access'
            )
            read_access = found_file[u"access"].get(C.ACCESS_PERM_READ, {})
            access_type = read_access.get(u'type', C.ACCESS_TYPE_WHITELIST)
            if access_type == C.ACCESS_TYPE_PUBLIC:
                field.values = [u'PUBLIC']
            else:
                field.values = read_access.get('jids', [])
            form.addField(field)
            if found_file[u'type'] == C.FILE_TYPE_DIRECTORY:
                field = data_form.Field(
                    "boolean", "recursive", value=False, required=False,
                    desc=u"Files under it will be made public to follow this dir "
                         u"permission (only if they don't have already a permission set)."
                )
                form.addField(field)

            status = self._c.STATUS.EXECUTING
            payload = form.toElement()
            defer.returnValue((payload, status, None, None))

        else:
            # final phase, we'll do permission change here
            try:
                read_allowed = command_form.fields['read_allowed']
            except KeyError:
                self._c.adHocError(self._c.ERROR.BAD_PAYLOAD)

            if read_allowed.value == u'PUBLIC':
                allowed_jids = u'PUBLIC'
            elif read_allowed.value.strip() == u'':
                allowed_jids = None
            else:
                try:
                    allowed_jids = [jid.JID(v.strip()) for v in read_allowed.values
                                    if v.strip()]
                except RuntimeError as e:
                    log.warning(_(u"Can't use read_allowed values: {reason}").format(
                        reason=e))
                    self._c.adHocError(self._c.ERROR.BAD_PAYLOAD)

            if found_file[u'type'] == C.FILE_TYPE_FILE:
                yield self.host.memory.fileUpdate(
                    found_file[u'id'], u'access',
                    partial(self._updateReadPermission, allowed_jids=allowed_jids))
            else:
                try:
                    recursive = command_form.fields['recursive']
                except KeyError:
                    self._c.adHocError(self._c.ERROR.BAD_PAYLOAD)
                yield self.host.memory.fileUpdate(
                    found_file[u'id'], u'access',
                    partial(self._updateReadPermission, allowed_jids=allowed_jids))
                if recursive:
                    # we set all file under the directory as public (if they haven't
                    # already a permission set), so allowed entities of root directory
                    # can read them.
                    namespace = session_data[u'namespace']
                    yield self._updateDir(
                        client, requestor_bare, namespace, found_file, u'PUBLIC')

            # job done, we can end the session
            status = self._c.STATUS.COMPLETED
            payload = None
            note = (self._c.NOTE.INFO, _(u"management session done"))
            defer.returnValue((payload, status, None, note))

    @defer.inlineCallbacks
    def _onDeleteFile(self, client, command_elt, session_data, action, node):
        try:
            x_elt = command_elt.elements(data_form.NS_X_DATA, "x").next()
            command_form = data_form.Form.fromElement(x_elt)
        except StopIteration:
            command_form = None

        found_file = session_data.get('found_file')
        requestor = session_data[u'requestor']
        requestor_bare = requestor.userhostJID()

        if command_form is None or len(command_form.fields) == 0:
            # root request
            defer.returnValue(self._getRootArgs())

        elif found_file is None:
            # file selected, we need confirmation before actually deleting
            try:
                found_file = yield self._getFileData(client, session_data, command_form)
            except WorkflowError as e:
                defer.returnValue(e.err_args)
            if found_file[u'type'] == C.FILE_TYPE_DIRECTORY:
                msg = D_(u"Are you sure to delete directory {name} and all files and "
                         u"directories under it?").format(name=found_file[u'name'])
            else:
                msg = D_(u"Are you sure to delete file {name}?"
                    .format(name=found_file[u'name']))
            form = data_form.Form("form", title=u"File Management",
                                  instructions = [msg],
                                  formNamespace=NS_FILE_MANAGEMENT)
            field = data_form.Field(
                "boolean", "confirm", value=False, required=True,
                desc=u"check this box to confirm"
            )
            form.addField(field)
            status = self._c.STATUS.EXECUTING
            payload = form.toElement()
            defer.returnValue((payload, status, None, None))

        else:
            # final phase, we'll do deletion here
            try:
                confirmed = command_form.fields['confirm']
            except KeyError:
                self._c.adHocError(self._c.ERROR.BAD_PAYLOAD)
            if not confirmed:
                note = None
            else:
                recursive = found_file[u'type'] == C.FILE_TYPE_DIRECTORY
                yield self.host.memory.fileDelete(
                    client, requestor_bare, found_file[u'id'], recursive)
                note = (self._c.NOTE.INFO, _(u"file deleted"))
            status = self._c.STATUS.COMPLETED
            payload = None
            defer.returnValue((payload, status, None, note))

    def _updateThumbs(self, extra, thumbnails):
        extra[C.KEY_THUMBNAILS] = thumbnails

    @defer.inlineCallbacks
    def _genThumbs(self, client, requestor, namespace, file_data):
        """Recursively generate thumbnails

        @param file_data(dict): metadata of the file
        """
        if file_data[u'type'] == C.FILE_TYPE_DIRECTORY:
            sub_files_data = yield self.host.memory.getFiles(
                client, requestor, parent=file_data[u'id'], namespace=namespace)
            for sub_file_data in sub_files_data:
                yield self._genThumbs(client, requestor, namespace, sub_file_data)

        elif file_data[u'type'] == C.FILE_TYPE_FILE:
            mime_type = file_data[u'mime_type']
            file_path = os.path.join(self.files_path, file_data[u'file_hash'])
            if mime_type is not None and mime_type.startswith(u"image"):
                thumbnails = []

                for max_thumb_size in (self._t.SIZE_SMALL, self._t.SIZE_MEDIUM):
                    try:
                        thumb_size, thumb_id = yield self._t.generateThumbnail(
                            file_path,
                            max_thumb_size,
                            #  we keep thumbnails for 6 months
                            60 * 60 * 24 * 31 * 6,
                        )
                    except Exception as e:
                        log.warning(_(u"Can't create thumbnail: {reason}")
                            .format(reason=e))
                        break
                    thumbnails.append({u"id": thumb_id, u"size": thumb_size})

                yield self.host.memory.fileUpdate(
                    file_data[u'id'], u'extra',
                    partial(self._updateThumbs, thumbnails=thumbnails))

                log.info(u"thumbnails for [{file_name}] generated"
                    .format(file_name=file_data[u'name']))

        else:
            log.warning(u"unmanaged file type: {type_}".format(type_=file_data[u'type']))

    @defer.inlineCallbacks
    def _onGenThumbnails(self, client, command_elt, session_data, action, node):
        try:
            x_elt = command_elt.elements(data_form.NS_X_DATA, "x").next()
            command_form = data_form.Form.fromElement(x_elt)
        except StopIteration:
            command_form = None

        found_file = session_data.get('found_file')
        requestor = session_data[u'requestor']

        if command_form is None or len(command_form.fields) == 0:
            # root request
            defer.returnValue(self._getRootArgs())

        elif found_file is None:
            # file selected, we retrieve it and ask for permissions
            try:
                found_file = yield self._getFileData(client, session_data, command_form)
            except WorkflowError as e:
                defer.returnValue(e.err_args)

            log.info(u"Generating thumbnails as requested")
            yield self._genThumbs(client, requestor, found_file[u'namespace'], found_file)

            # job done, we can end the session
            status = self._c.STATUS.COMPLETED
            payload = None
            note = (self._c.NOTE.INFO, _(u"thumbnails generated"))
            defer.returnValue((payload, status, None, note))

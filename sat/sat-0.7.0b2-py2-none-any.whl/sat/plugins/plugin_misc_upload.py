#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for file tansfer
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from sat.tools import xml_tools
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from twisted.words.protocols.jabber import error as jabber_error
import os
import os.path


PLUGIN_INFO = {
    C.PI_NAME: "File Upload",
    C.PI_IMPORT_NAME: "UPLOAD",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MAIN: "UploadPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""File upload management"""),
}


UPLOADING = D_(u"Please select a file to upload")
UPLOADING_TITLE = D_(u"File upload")
BOOL_OPTIONS = ("ignore_tls_errors",)


class UploadPlugin(object):
    # TODO: plugin unload

    def __init__(self, host):
        log.info(_("plugin Upload initialization"))
        self.host = host
        host.bridge.addMethod(
            "fileUpload",
            ".plugin",
            in_sign="sssa{ss}s",
            out_sign="a{ss}",
            method=self._fileUpload,
            async=True,
        )
        self._upload_callbacks = []

    def _fileUpload(
        self, filepath, filename, upload_jid_s="", options=None, profile=C.PROF_KEY_NONE
    ):
        client = self.host.getClient(profile)
        upload_jid = jid.JID(upload_jid_s) if upload_jid_s else None
        if options is None:
            options = {}
        # we convert values that are well-known booleans
        for bool_option in BOOL_OPTIONS:
            try:
                options[bool_option] = C.bool(options[bool_option])
            except KeyError:
                pass

        return self.fileUpload(
            client, filepath, filename or None, upload_jid, options or None
        )

    def fileUpload(self, client, filepath, filename, upload_jid, options):
        """Send a file using best available method

        parameters are the same as for [upload]
        @return (dict): action dictionary, with progress id in case of success, else xmlui
            message
        """

        def uploadCb(data):
            progress_id, __ = data
            return {"progress": progress_id}

        def uploadEb(fail):
            if (isinstance(fail.value, jabber_error.StanzaError)
                and fail.value.condition == 'not-acceptable'):
                reason = fail.value.text
            else:
                reason = unicode(fail.value)
            msg = D_(u"Can't upload file: {reason}").format(reason=reason)
            log.warning(msg)
            return {
                "xmlui": xml_tools.note(
                    msg, D_(u"Can't upload file"), C.XMLUI_DATA_LVL_WARNING
                ).toXml()
            }

        d = self.upload(client, filepath, filename, upload_jid, options)
        d.addCallback(uploadCb)
        d.addErrback(uploadEb)
        return d

    @defer.inlineCallbacks
    def upload(self, client, filepath, filename=None, upload_jid=None, options=None):
        """Send a file using best available method

        @param filepath(str): absolute path to the file
        @param filename(None, unicode): name to use for the upload
            None to use basename of the path
        @param upload_jid(jid.JID, None): upload capable entity jid,
            or None to use autodetected, if possible
        @param options(dict): option to use for the upload, may be:
            - ignore_tls_errors(bool): True to ignore SSL/TLS certificate verification
                used only if HTTPS transport is needed
        @param profile: %(doc_profile)s
        @return (tuple[unicode,D(unicode)]): progress_id and a Deferred which fire
            download URL when upload is finished
        """
        if options is None:
            options = {}
        if not os.path.isfile(filepath):
            raise exceptions.DataError(u"The given path doesn't link to a file")
        for method_name, available_cb, upload_cb, priority in self._upload_callbacks:
            try:
                upload_jid = yield available_cb(upload_jid, client.profile)
            except exceptions.NotFound:
                continue  # no entity managing this extension found

            log.info(
                u"{name} method will be used to upload the file".format(name=method_name)
            )
            progress_id_d, download_d = yield upload_cb(
                filepath, filename, upload_jid, options, client.profile
            )
            progress_id = yield progress_id_d
            defer.returnValue((progress_id, download_d))

        raise exceptions.NotFound(u"Can't find any method to upload a file")

    def register(self, method_name, available_cb, upload_cb, priority=0):
        """Register a fileUploading method

        @param method_name(unicode): short name for the method, must be unique
        @param available_cb(callable): method to call to check if this method is usable
           the callback must take two arguments: upload_jid (can be None) and profile
           the callback must return the first entity found (being upload_jid or one of its
           components)
           exceptions.NotFound must be raised if no entity has been found
        @param upload_cb(callable): method to upload a file
            must have the same signature as [fileUpload]
            must return a tuple with progress_id and a Deferred which fire download URL
            when upload is finished
        @param priority(int): pririoty of this method, the higher available will be used
        """
        assert method_name
        for data in self._upload_callbacks:
            if method_name == data[0]:
                raise exceptions.ConflictError(
                    u"A method with this name is already registered"
                )
        self._upload_callbacks.append((method_name, available_cb, upload_cb, priority))
        self._upload_callbacks.sort(key=lambda data: data[3], reverse=True)

    def unregister(self, method_name):
        for idx, data in enumerate(self._upload_callbacks):
            if data[0] == method_name:
                del [idx]
                return
        raise exceptions.NotFound(u"The name to unregister doesn't exist")
